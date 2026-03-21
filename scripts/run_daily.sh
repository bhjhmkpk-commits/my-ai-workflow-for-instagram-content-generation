#!/usr/bin/env bash
set -euo pipefail

cd /home/bohar/instagram-short-generator
source .venv/bin/activate
PYTHONPATH=src python -m shortgen.cli run
