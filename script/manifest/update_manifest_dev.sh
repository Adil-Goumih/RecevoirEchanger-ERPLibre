#!/usr/bin/env bash

. ./env_var.sh

#EL_MANIFEST_PROD="./default.xml"
#EL_MANIFEST_DEV="./manifest/default.dev.xml"

# Update git-repo
./.venv/repo init -u https://github.com/OffrirRecevoirEchanger/ERPLibre -b $(git rev-parse --verify HEAD) -m ${EL_MANIFEST_DEV}
#./.venv/repo sync --force-sync
./.venv/repo sync --force-sync -v
