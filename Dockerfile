FROM ghcr.io/openaleph/ingest-file-base

RUN apt update ; apt install -y git

COPY . /ingestors
WORKDIR /ingestors
RUN pip3 install -r /ingestors/requirements.txt
RUN pip3 install --no-cache-dir --config-settings editable_mode=compat --use-pep517 /ingestors
RUN chown -R app:app /ingestors


ENV ARCHIVE_TYPE=file \
    ARCHIVE_PATH=/data \
    FTM_STORE_URI=postgresql://aleph:aleph@postgres/aleph \
    REDIS_URL=redis://redis:6379/0 \
    TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata

ENV LD_PRELOAD="/usr/lib/x86_64-linux-gnu/libgomp.so.1"

# USER app
CMD ingestors process
