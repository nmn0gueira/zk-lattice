#!/usr/bin/env bash
set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

git -C "${REPO_DIR}" submodule update --init 2>/dev/null || true

cd "${REPO_DIR}/lazer"

git -C "${REPO_DIR}/lazer" submodule update --init src/labrados 2>/dev/null || true


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

LAZER_MAKE_TARGET=$([ "${LAZER_AVX512:-0}" = "1" ] && echo "all" || echo "liblazer.so liblazer.a")
make ${LAZER_MAKE_TARGET} -j"$(nproc)"
cd python && make
