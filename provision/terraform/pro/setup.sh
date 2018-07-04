#!/bin/sh
CURRENT_DIR="$(cd "$(dirname "${0}")" && pwd)"

set -x

cd "${CURRENT_DIR}"
SECS="3"
while :; do
    terraform init  && \
    terraform plan  && \
    terraform apply && break

    printf "%s\\n" "respawing in ${SECS} secs ..."
    sleep "${SECS}"
done
