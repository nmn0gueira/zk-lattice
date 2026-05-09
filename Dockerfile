FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/opt/miniforge/envs/lazer/bin:/opt/miniforge/bin:${PATH}"

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    wget \
    unzip \
    libgmp-dev \
    libmpfr-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN wget https://github.com/conda-forge/miniforge/releases/download/26.1.1-3/Miniforge3-Linux-x86_64.sh \
        -O /tmp/miniforge.sh && \
    bash /tmp/miniforge.sh -b -p /opt/miniforge && \
    rm /tmp/miniforge.sh && \
    /opt/miniforge/bin/conda clean --all -y

RUN /opt/miniforge/bin/mamba create -y -n lazer \
    python=3.10 \
    "sage=10.2" \
    cffi \
    sphinx \
    sphinxcontrib-bibtex

# mpmath 1.4.x breaks sage 10.2: strict gmpy2.mpz assertion fails for sage integers.
# Pin to 1.3.0 which uses Python int (compatible).
RUN /opt/miniforge/envs/lazer/bin/pip install --force-reinstall "mpmath==1.3.0"
