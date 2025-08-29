FROM python:3.11-slim

# Install system dependencies needed for thruster testing
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    pkg-config \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy the application
COPY app /app

# Install Python dependencies
RUN python -m pip install --upgrade pip && \
    python -m pip install flask flask-cors minimalmodbus gpiozero requests pyserial

# Install Blue Robotics packages using the working Jupyter method
RUN pip install --no-cache-dir --verbose \
    bluerobotics-ping \
    bluerobotics-navigator

# Copy the app files directly instead of installing in editable mode
RUN cp -r /app/backend /app/backend_copy && \
    cp -r /app/frontend /app/frontend_copy && \
    cp -r /app/static /app/static_copy && \
    cp /app/main.py /app/main_copy.py && \
    cp /app/pyproject.toml /app/pyproject_copy.toml

EXPOSE 8001/tcp

LABEL version="0.0.1"

ARG IMAGE_NAME

LABEL permissions='\
{\
  "NetworkMode": "host",\
  "HostConfig": {\
    "Privileged": true,\
    "Binds": [\
      "/usr/blueos/extensions/brthrusterdestroyer/root:/root:rw",\
      "/dev:/dev:rw"\
    ],\
    "Privileged": true,\
    "NetworkMode": "host"\
  }\
}'

ARG AUTHOR
ARG AUTHOR_EMAIL
LABEL authors='[\
    {\
        "name": "$AUTHOR",\
        "email": "$AUTHOR_EMAIL"\
    }\
]'

ARG MAINTAINER
ARG MAINTAINER_EMAIL
LABEL company='{\
        "about": "Thruster Testing and Data Logging Extension",\
        "name": "$MAINTAINER",\
        "email": "$MAINTAINER_EMAIL"\
    }'
LABEL type="extension"
ARG REPO
ARG OWNER
LABEL readme='https://raw.githubusercontent.com/$OWNER/$REPO/{tag}/README.md'
LABEL links='{\
        "source": "https://github.com/$OWNER/$REPO"\
    }'
LABEL requirements="core >= 1.1"

# Set the working directory and run the Flask app
WORKDIR /app
CMD ["python", "main_copy.py"]