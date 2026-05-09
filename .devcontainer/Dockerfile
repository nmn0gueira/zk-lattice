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

# Miniforge
RUN wget https://github.com/conda-forge/miniforge/releases/download/26.1.1-3/Miniforge3-Linux-x86_64.sh \
        -O /tmp/miniforge.sh && \
    bash /tmp/miniforge.sh -b -p /opt/miniforge && \
    rm /tmp/miniforge.sh && \
    /opt/miniforge/bin/conda clean --all -y

# Python-only tooling
RUN /opt/miniforge/bin/mamba create -y -n lazer \
    python=3.10 \
    "sage=10.2" \
    cffi \
    sphinx \
    sphinxcontrib-bibtex

# mpmath 1.4.x is incompatible with sage 10.2: it uses gmpy2.mpz as its internal
# integer type, but sage's arithmetic routines produce sage.rings.integer.Integer
# values that cannot coerce to/from gmpy2.mpz within mpmath's C extensions.
# Sage 10.2 was released before mpmath 1.4 and has no fix for this.
# Force-install 1.3.0 via pip, which uses Python int (compatible with sage integers).
RUN /opt/miniforge/envs/lazer/bin/pip install --force-reinstall "mpmath==1.3.0"
