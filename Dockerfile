FROM enclave_base
WORKDIR /app

# update system and install python 3.12 deps
RUN yum update -y && \
    yum install -y gcc iproute openssl-devel bzip2-devel libffi-devel \
    zlib-devel wget tar gzip make

# add rpmfusion for py3.12
RUN dnf install -y python3.12

# get uv (way cleaner than pip)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    echo 'export PATH="/root/.cargo/bin:$PATH"' >> ~/.bashrc


# copy your app code
COPY . /app/

# use uv to set up deps (way faster than pip)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    /root/.local/bin/uv venv -p python3.12 --seed && \
    /root/.local/bin/uv pip install -e ".[dev]"


# rest of your setup
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]