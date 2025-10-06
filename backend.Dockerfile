# what to install
FROM python:3.12-alpine3.21

LABEL maintainer=""
LABEL version="1.0"
LABEL description="Python 3.12 (Linux) Alpine 3.21"

# install image-folder
WORKDIR /usr/src/app

COPY . .

# install dependencies
RUN apk add --no-cache bash postgresql-client ffmpeg \
    && apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev python3-dev \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del .build-deps \
    && chmod +x backend.entrypoint.sh

EXPOSE 8000

ENTRYPOINT [ "./backend.entrypoint.sh" ]