#!/usr/bin/env bash
set -euo pipefail

cd /home/bohar/instagram-short-generator

if [[ "${SHORTGEN_DISABLE_TTS:-false}" == "true" ]]; then
  export NVIDIA_TTS_SCRIPT_PATH=""
fi

PYTHONPATH=src python -m shortgen.cli run
