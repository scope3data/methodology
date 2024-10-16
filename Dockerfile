# Use the official lightweight Python image.
FROM python:3.10
# Allow statements and log
ENV PYTHONUNBUFFERED=True

RUN mkdir /app
WORKDIR /app
COPY . ./
COPY pyproject.toml /app

ENV PYTHONPATH=/app
RUN pip install -r requirements.txt

RUN python "./scope3_methodology/cli/compute_defaults.py"
ENV ATP_DEFAULTS_FILE=/app/defaults/atp-defaults.yaml
ENV ORGANIZATION_DEFAULTS_FILE=/app/defaults/organization-defaults.yaml
ENV PROPERTY_DEFAULTS_FILE=/app/defaults/property-defaults.yaml
ENV END_USER_DEVICE_DEFAULTS_FILE=/app/defaults/end_user_device-defaults.yaml
ENV NETWORKING_DEFAULTS_FILE=/app/defaults/networking-defaults.yaml
ENV TRANSMISSION_RATE_FILE=/app/defaults/transmission_rate-defaults.yaml
ENV DOCS_DEFAULTS_FILE=/app/defaults/docs-defaults.yaml

CMD ["python", "scope3_methodology/api/api.py"]
