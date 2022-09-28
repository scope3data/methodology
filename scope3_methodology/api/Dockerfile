# Use the official lightweight Python image.
FROM python:3.9-slim
# Allow statements and log
ENV PYTHONUNBUFFERED True
# Copy local code to the container image.
ENV APP_HOME /scope3_methodology/
WORKDIR $APP_HOME
COPY . ./
# Install production dependencies.
RUN pip install -r requirements.txt
# Run
CMD ["python", "api.py"]