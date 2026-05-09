# zk-lattice

Lattice-based zero-knowledge proof prototypes built on the [lazer](https://github.com/lazer-crypto/lazer) library.

## Setup

```bash
git clone https://github.com/nmn0gueira/zk-lattice.git
cd zk-lattice
git submodule update --init
```

Build the image and lazer library:

```bash
docker build -t zk-lattice .
docker run --rm -v $(pwd):/workspaces/code zk-lattice bash /workspaces/code/build.sh

# With AVX-512 support (requires a compatible CPU):
docker run --rm -v $(pwd):/workspaces/code -e LAZER_AVX512=1 zk-lattice bash /workspaces/code/build.sh
```

Then open an interactive shell to explore:

```bash
docker run --rm -it -v $(pwd):/workspaces/code -w /workspaces/code zk-lattice bash
```

## Running

Each protocol lives under `protos/<name>/` with its own `Makefile`.

```bash
cd protos/linrel  && make run           # linear relation demo
cd protos/leopard && make run           # LeoPaRd NIZKs (ternary witnesses)
cd protos/leopard && make run-gaussian  # LeoPaRd NIZKs (Gaussian witnesses)
```

## Adding a new protocol

```
protos/<name>/
  params.py          # lin-codegen spec (vname, deg, mod, dim, wpart, wl2, wbin, wlinf)
  demo.py            # proof / verify script
  Makefile           # see protos/linrel/Makefile for the template
```

Run `make` to generate `params.h` and build the CFFI extension, then `make run`.