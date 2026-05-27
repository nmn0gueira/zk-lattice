#!/usr/bin/env bash
set -e

# TODO: Remove these adds and make script docker-agnostic
git config --global --add safe.directory /workspaces/code
git config --global --add safe.directory /workspaces/code/lazer
git config --global --add safe.directory /workspaces/code/lazer/src/labrador

git -C /workspaces/code submodule update --init 2>/dev/null || true

cd /workspaces/code/lazer

# labrador's .gitmodules entry uses SSH. We rewrite to HTTPS so Docker doesn't prompt for credentials.
git -C /workspaces/code/lazer config submodule.src/labrador.url https://github.com/lattice-dogs/labrador 2>/dev/null || true
git -C /workspaces/code/lazer submodule update --init src/labrador 2>/dev/null || true


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
