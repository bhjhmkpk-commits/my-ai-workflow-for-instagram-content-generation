#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_ROOT}"

if [[ "${SHORTGEN_DISABLE_TTS:-false}" == "true" ]]; then
  export NVIDIA_TTS_SCRIPT_PATH=""
fi

PYTHONPATH=src python -m shortgen.cli run
