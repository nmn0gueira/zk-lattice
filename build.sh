#!/usr/bin/env bash
set -e

git -C /workspaces/code submodule update --init 2>/dev/null || true

cd /workspaces/code/lazer

# labrador's .gitmodules entry uses SSH. We rewrite to HTTPS so Docker doesn't prompt for credentials.
git config submodule.src/labrador.url https://github.com/lattice-dogs/labrador

# First pass unpacks Falcon/HEXL and runs cmake for HEXL.
# MAKEFLAGS cleared to avoid inheriting the outer jobserver FIFO (absent in Docker).
MAKEFLAGS= make || true

# cmake puts libhexl.a in lib/ on Debian but the Makefile expects lib64/.
HEXL_BUILD=third_party/hexl-development/build/hexl
if [ ! -f "${HEXL_BUILD}/lib64/libhexl.a" ]; then
    found=$(find "${HEXL_BUILD}" -name "libhexl.a" 2>/dev/null | head -1)
    if [ -n "$found" ]; then
        mkdir -p "${HEXL_BUILD}/lib64"
        ln -sf "$(realpath --relative-to="${HEXL_BUILD}/lib64" "$found")" \
            "${HEXL_BUILD}/lib64/libhexl.a"
        echo "Created lib64 symlink -> $found"
    fi
fi

LAZER_MAKE_TARGET=$([ "${LAZER_AVX512:-0}" = "1" ] && echo "all" || echo "")
make ${LAZER_MAKE_TARGET} -j"$(nproc)"
cd python && make
