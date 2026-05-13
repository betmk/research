#!/bin/bash
# Wrapper for setup_premium_auth.py — keeps everything inside the venv.
set -e
REPO_ROOT="/Users/mikemadden/Desktop/Claude Projects/research"
cd "$REPO_ROOT"
.venv/bin/python scripts/setup_premium_auth.py "$@"
