FROM ubuntu:22.04

RUN apt update -y && \
    apt install -y curl

RUN DKF_CLI_VERSION="0.1.2" && \
    DKF_CLI_ARCH=$(uname -m | sed -e 's/x86_64/amd64/' -e 's/aarch64/arm64/') && \
    DFK_CLI_DEST=/usr/local/bin/deploykf && \
    curl -fL "https://github.com/deploykf/cli/releases/download/v${DKF_CLI_VERSION}/deploykf-linux-${DKF_CLI_ARCH}" -o "${DFK_CLI_DEST}" && \
    chmod +x "${DFK_CLI_DEST}"

COPY custom-values.yaml /tmp/custom-values.yaml
