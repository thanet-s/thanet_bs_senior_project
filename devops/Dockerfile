FROM debian:11-slim

ARG K6_VERSION="v0.43.1"

# Install basic development tools
RUN apt-get update && \
  apt-get install -y curl python3-dev python3-pip sshpass rsync && \
  pip3 install --no-cache-dir --upgrade pip && \
  pip3 install --no-cache-dir ansible==7.3.0 docker==6.0.1 kubernetes==26.1.0 jsonpatch==1.32 \
  && rm -rf /var/lib/apt/lists/*

# Download k6
RUN if [ $(uname -m) = "x86_64" ]; then \
      curl -L --show-error https://github.com/grafana/k6/releases/download/${K6_VERSION}/k6-${K6_VERSION}-linux-amd64.tar.gz | tar -xz -C /usr/local/bin --strip-components=1; \
    elif [ $(uname -m) = "aarch64" ]; then \
      curl -L --show-error https://github.com/grafana/k6/releases/download/${K6_VERSION}/k6-${K6_VERSION}-linux-arm64.tar.gz | tar -xz -C /usr/local/bin --strip-components=1; \
    else \
      echo "Unsupported CPU architecture: $(uname -m)"; exit 1; \
    fi && \
    chmod +x /usr/local/bin/k6

RUN mkdir -p /devops
WORKDIR /devops

CMD ["/bin/bash"]
