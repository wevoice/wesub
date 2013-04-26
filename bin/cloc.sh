#!/usr/bin/env bash

set -e

# Finding files we may want to ignore:
# cloc \
#     --exclude-dir='third-party,rosetta,redisco,kombu_backends,migrations' \
#     --not-match-f='jquery-.*.js' \
#     . --by-file --csv \
#     | grep Python \
#     | cut -d , -f 2- \
#     | sort -n -t, -k2

cloc \
    --exclude-dir='third-party,rosetta,redisco,kombu_backends,migrations' \
    --not-match-f='jquery-.*.js' \
    .
