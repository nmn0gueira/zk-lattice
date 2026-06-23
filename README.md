# zk-lattice

Lattice-based zero-knowledge proof prototypes built on the [lazer](https://github.com/lazer-crypto/lazer) library.

## Setup

### Docker

```bash
git clone --recurse-submodules https://github.com/nmn0gueira/zk-lattice.git
cd zk-lattice
docker build -t zk-lattice .
docker run -it zk-lattice bash
```

For AVX-512 support (requires a compatible CPU):

```bash
docker build --build-arg LAZER_AVX512=1 -t zk-lattice .
```

### Native (Linux)

```bash
git clone https://github.com/nmn0gueira/zk-lattice.git
cd zk-lattice
bash build.sh
```

## Running

Each protocol lives under `protos/<name>/` with its own `Makefile`.

```bash
cd protos/linrel   && make run           # linear relation demo (lin_prover, d=256)
cd protos/linrel   && make run-labrador  # same relation with LaBRADOR (d=64, requires AVX-512 build)
cd protos/leopard  && make run           # LeoPaRd NIZKs (ternary witnesses)
cd protos/leopard  && make run-gaussian  # LeoPaRd NIZKs (Gaussian witnesses)
```

## Adding a new protocol

```
protos/<name>/
  params.py          # lin-codegen spec (vname, deg, mod, dim, wpart, wl2, wbin, wlinf)
  demo.py            # proof / verify script
  Makefile           # see protos/linrel/Makefile for the template
```

Run `make` to generate `params.h` and build the CFFI extension, then `make run`.