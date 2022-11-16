import os
import time
from ingestors.log import get_logger
import subprocess
from psutil import process_iter, TimeoutExpired, NoSuchProcess

from convert.util import CONVERT_DIR, flush_path, MAX_TIMEOUT
from convert.util import ConversionFailure

OUT_DIR = os.path.join(CONVERT_DIR, "out")
log = get_logger(__name__)


class ProcessConverter:
    def check_healthy(self):
        proc = self.get_proc()
        if proc is None:
            return True
        timed_out = time.time() - MAX_TIMEOUT
        if proc.create_time() > timed_out:
            return True
        return False

    def prepare(self):
        self.kill()
        flush_path(CONVERT_DIR)
        flush_path(OUT_DIR)

    def convert_file(self, file_name, timeout):
        cmd = [
            "/usr/bin/libreoffice",
            '"-env:UserInstallation=file:///tmp"',
            "--nologo",
            "--headless",
            "--nocrashreport",
            "--nodefault",
            "--norestore",
            "--nolockcheck",
            "--invisible",
            "--convert-to",
            "pdf",
            "--outdir",
            OUT_DIR,
            file_name,
        ]
        try:
            log.info("Starting LibreOffice: %s with timeout %s", cmd, timeout)
            subprocess.run(cmd, timeout=timeout)

            for file_name in os.listdir(OUT_DIR):
                if not file_name.endswith(".pdf"):
                    continue
                out_file = os.path.join(OUT_DIR, file_name)
                if os.stat(out_file).st_size == 0:
                    continue
                return out_file
        except subprocess.SubprocessError:
            log.exception("LibreOffice conversion failed")
            self.kill()

        raise ConversionFailure("Cannot generate PDF.")

    def kill(self):
        # The Alfred Hitchcock approach to task management:
        # https://www.youtube.com/watch?v=0WtDmbr9xyY
        for i in range(10):
            proc = self.get_proc()
            if proc is None:
                break
            log.info("Disposing converter process.")
            try:
                proc.kill()
                proc.wait(timeout=10)
            except NoSuchProcess:
                log.info("Process has disappeared")
            except (TimeoutExpired, Exception) as exc:
                log.error("Failed to kill: %r (%s)", proc, exc)
                os._exit(23)

    def get_proc(self):
        for proc in process_iter(["cmdline", "create_time"]):
            name = " ".join(proc.cmdline())
            if "soffice.bin" in name:
                return proc
