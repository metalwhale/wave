# See: https://www.kubeflow.org/docs/components/notebooks/container-images/#base-images

FROM kubeflownotebookswg/codeserver:v1.8.0

USER root

RUN apt update -y && \
    apt install sudo && \
    echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
RUN adduser $NB_USER sudo

USER $NB_USER
