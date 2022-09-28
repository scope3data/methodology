# Use the official lightweight Python image.
FROM python:3.10
# Allow statements and log
ENV PYTHONUNBUFFERED True

RUN mkdir /app
WORKDIR /app
COPY . ./
COPY pyproject.toml /app

ENV PYTHONPATH=${PYTHONPATH}:${PWD}
RUN pip install -r requirements.txt

RUN  python "./scope3_methodology/cli/compute_defaults.py"
ENV ATP_DEFAULTS_FILE /app/atp-defaults.yaml
ENV ORGANIZATION_DEFAULTS_FILE /app/organization-defaults.yaml
ENV PROPERTY_DEFAULTS_FILE /app/property-defaults.yaml

CMD ["python", "scope3_methodology/api/api.py"]
