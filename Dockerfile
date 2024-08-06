# syntax=docker/dockerfile:1

# heet_cli.py requires Python 3.8
ARG PYTHON_VERSION=3.8.18
FROM python:${PYTHON_VERSION}-slim as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

# Install the gcloud cli
RUN apt-get update -y
RUN apt install curl -y
ENV PATH=/google-cloud-sdk/bin:$PATH
WORKDIR /
RUN export CLOUD_SDK_VERSION="410.0.0" && \
    curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-${CLOUD_SDK_VERSION}-linux-x86_64.tar.gz && \
    tar xzf google-cloud-sdk-${CLOUD_SDK_VERSION}-linux-x86_64.tar.gz && \
    rm google-cloud-sdk-${CLOUD_SDK_VERSION}-linux-x86_64.tar.gz && \
    ln -s /lib /lib64

# Create a non-privileged user that the app will run under.
RUN useradd --create-home --shell /bin/bash appuser

# Install Python depdenencies
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

# Switch to the non-privileged user to run the application.
USER appuser

# Create a folder for GeoCARET
RUN mkdir -p /home/appuser/geocaret
WORKDIR /home/appuser/geocaret

# Copy the source code into the container.
COPY --chown=appuser:appuser . .

# Execute the user-specified command line arguments.
ENTRYPOINT [ "/bin/bash", "./docker_entrypoint.sh" ]

# Default command if no arguments supplied 
CMD [ "echo", "You must specify a command to run. See You must specify a command to run. See https://Reservoir-Research.github.io/geocaret/running_geocaret/running_docker.html for details." ]

# https://Reservoir-Research.github.io/reemission/
