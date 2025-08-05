# syntax=docker/dockerfile:1.7
# Harborline Book API image. Build with:
#   DOCKER_BUILDKIT=1 docker build --secret id=gh_token,env=GH_TOKEN -t harborline/api .

FROM python:3.12-slim AS build
ENV PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
RUN apt-get update && apt-get install -y --no-install-recommends git build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /src
COPY requirements.txt .
RUN pip wheel --wheel-dir /wheels -r requirements.txt
# hbl-geo is a private package; the token is mounted as a BuildKit secret and never
# lands in an image layer or in `docker history`.
RUN --mount=type=secret,id=gh_token GH_TOKEN=$(cat /run/secrets/gh_token) \
    pip wheel --wheel-dir /wheels "git+https://x-access-token:${GH_TOKEN}@github.com/harborline-freight/hbl-geo.git@v0.4.2"

FROM python:3.12-slim AS runtime
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 10001 harborline
WORKDIR /app
COPY --from=build /wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels
COPY --chown=harborline:harborline . .
USER harborline
ENV HBL_ENV=production PORT=8080
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/healthz')"
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "3", "--access-logfile", "-", "wsgi:app"]
