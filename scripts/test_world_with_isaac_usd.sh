#!/usr/bin/env bash
set -euo pipefail

CBNU_ISAAC_ROOT="${CBNU_ISAAC_ROOT:-/home/a/isaacsim}"
CBNU_USD_EXT=""

for CBNU_CANDIDATE in "${CBNU_ISAAC_ROOT}"/extscache/omni.usd.libs-*; do
    if [[ -d "${CBNU_CANDIDATE}/pxr" ]]; then
        CBNU_USD_EXT="${CBNU_CANDIDATE}"
        break
    fi
done

if [[ -z "${CBNU_USD_EXT}" ]]; then
    echo "Isaac Sim omni.usd.libs extension not found under ${CBNU_ISAAC_ROOT}" >&2
    exit 1
fi

CBNU_REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

env \
    PYTHONPATH="${CBNU_USD_EXT}" \
    LD_LIBRARY_PATH="${CBNU_USD_EXT}/bin:${CBNU_ISAAC_ROOT}/kit" \
    PXR_PLUGINPATH_NAME="${CBNU_USD_EXT}/bin/usd" \
    "${CBNU_ISAAC_ROOT}/kit/python/bin/python3" \
    "${CBNU_REPO_ROOT}/scripts/test_world.py"
