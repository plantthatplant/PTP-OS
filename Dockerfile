# Gaia API — stdlib Python only, no dependencies → a tiny, fast image.
FROM python:3.12-slim

WORKDIR /app
COPY . /app

# Bind all interfaces inside the container; the platform terminates TLS and maps the port.
# GAIA_PORT (or a host-injected $PORT) selects the listen port; default 8000.
ENV GAIA_HOST=0.0.0.0 \
    PYTHONUNBUFFERED=1

# Persist Memory / Learning / Observations + snapshots on a mounted volume in production:
#   GAIA_DATA_DIR=/data  GAIA_APP_DATA_DIR=/data/app
EXPOSE 8000

# The supervisor: serves the API and collects snapshots on a schedule. Loads secrets from the
# environment (set them as platform secrets, never baked into the image).
CMD ["python", "-m", "api.run"]
