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

# Install Python dependencies first (without the problematic ones)
RUN python -m pip install --upgrade pip && \
    python -m pip install litestar[standard] minimalmodbus gpiozero requests pyserial

# Install Blue Robotics Navigator from source (if available)
RUN python -m pip install git+https://github.com/bluerobotics/blueos-python.git#subdirectory=blueos-python-navigator || \
    echo "Navigator package not available, will use fallback methods"

# Install the app in development mode
RUN python -m pip install -e /app

EXPOSE 8000/tcp

LABEL version="0.0.1"

ARG IMAGE_NAME

LABEL permissions='\
{\
  "ExposedPorts": {\
    "8000/tcp": {}\
  },\
  "HostConfig": {\
    "Binds":["/usr/blueos/extensions/$IMAGE_NAME:/app"],\
    "ExtraHosts": ["host.docker.internal:host-gateway"],\
    "PortBindings": {\
      "8000/tcp": [\
        {\
          "HostPort": ""\
        }\
      ]\
    },\
    "Devices": [\
      "/dev/ttyUSB0:/dev/ttyUSB0",\
      "/dev/gpiomem:/dev/gpiomem"\
    ],\
    "Privileged": true\
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

ENTRYPOINT ["litestar", "run", "--host", "0.0.0.0"]
