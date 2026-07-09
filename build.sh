#!/usr/bin/env bash
set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

git -C "${REPO_DIR}" submodule update --init 2>/dev/null || true

cd "${REPO_DIR}/lazer"

git -C "${REPO_DIR}/lazer" submodule update --init src/labrados 2>/dev/null || true


make liblazer.so liblazer.a

if [ "${LAZER_AVX512:-0}" = "1" ]; then
    HEXL_BUILD=third_party/hexl-development/build/hexl
    if [ ! -f "${HEXL_BUILD}/lib64/libhexl.a" ]; then
        found=$(find "${HEXL_BUILD}" -name "libhexl.a" 2>/dev/null | head -1)
        if [ -n "$found" ]; then
            mkdir -p "${HEXL_BUILD}/lib64"
            ln -sf "$(realpath --relative-to="${HEXL_BUILD}/lib64" "$found")" \
                "${HEXL_BUILD}/lib64/libhexl.a"
        fi
    fi
    make all -j"$(nproc)"
fi

cd python && make
