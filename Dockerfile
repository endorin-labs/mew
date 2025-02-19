FROM enclave_base
WORKDIR /app

# --- Install build tools and Python 3.8 ---
RUN yum update -y && \
    yum install -y gcc iproute openssl-devel bzip2-devel libffi-devel zlib-devel wget tar gzip make

# Install Python 3.8 from amazon-linux-extras
RUN amazon-linux-extras install python3.8

# (Optional) Ensure python3.8 is in PATH. On Amazon Linux, it's typically in /usr/bin.
# ENV PATH="/usr/bin:${PATH}"

# --- Download, build, and install socat ---
RUN wget http://www.dest-unreach.org/socat/download/socat-1.8.0.2.tar.gz && \
    tar xzf socat-1.8.0.2.tar.gz && \
    cd socat-1.8.0.2 && \
    ./configure && \
    make && \
    make install && \
    cd .. && rm -rf socat-1.8.0.2 socat-1.8.0.2.tar.gz

# --- Copy Application Code ---
# This ensures that pyproject.toml, setup.py, and all other project files are present.
COPY . /app/

# --- Install uv and set up the virtual environment ---
# (Since the project files are now present, uv can detect the Python project)
RUN python3.8 -m pip install --upgrade pip && \
    python3.8 -m pip install uv && \
    uv venv -p python3.8 --seed && \
    uv pip install -e ".[dev]"

# --- Setup entrypoint ---
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
