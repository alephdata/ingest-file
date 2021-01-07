import os
import logging
from flask import Flask, request, send_file
from pantomime import FileName, normalize_mimetype, mimetype_extension
from pantomime.types import PDF

from convert.process import ProcessConverter
from convert.formats import load_mime_extensions
from convert.lock import FileLock
from convert.util import CONVERT_DIR, MAX_TIMEOUT
from convert.util import SystemFailure, ConversionFailure

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("convert")
app = Flask("convert")
lock = FileLock()
extensions = load_mime_extensions()
method = os.environ.get("CONVERTER_METHOD", "unoconv")
converter = ProcessConverter()


@app.route("/")
@app.route("/healthz")
@app.route("/health/live")
def check_health():
    try:
        if not converter.check_healthy():
            return ("DEAD", 503)
        return ("OK", 200)
    except Exception:
        log.exception("Converter is not healthy.")
        return ("DEAD", 503)


@app.route("/health/ready")
def check_ready():
    if lock.is_locked:
        return ("BUSY", 503)
    return ("OK", 200)


@app.route("/reset")
def reset():
    converter.kill()
    lock.unlock()
    return ("OK", 200)


@app.route("/convert", methods=["POST"])
def convert():
    upload_file = None
    if not lock.lock():
        return ("BUSY", 503)
    try:
        converter.prepare()
        timeout = int(request.args.get("timeout", MAX_TIMEOUT))
        upload = request.files.get("file")
        file_name = FileName(upload.filename)
        mime_type = normalize_mimetype(upload.mimetype)
        if not file_name.has_extension:
            file_name.extension = extensions.get(mime_type)
        if not file_name.has_extension:
            file_name.extension = mimetype_extension(mime_type)
        upload_file = os.path.join(CONVERT_DIR, file_name.safe())
        log.info("PDF convert: %s [%s]", upload_file, mime_type)
        upload.save(upload_file)
        out_file = converter.convert_file(upload_file, timeout)
        return send_file(out_file, mimetype=PDF)
    except ConversionFailure as ex:
        converter.kill()
        return (str(ex), 400)
    except Exception as ex:
        converter.kill()
        log.warning("Error: %s", ex)
        return (str(ex), 500)
    finally:
        lock.unlock()
