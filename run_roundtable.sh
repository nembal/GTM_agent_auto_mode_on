#!/usr/bin/env bash
# Run only the roundtable (ARTIST, BUSINESS, TECH). Uses weavehacks conda env.
set -e
cd "$(dirname "$0")"
conda run -n weavehacks python -m services.roundtable "$@"
