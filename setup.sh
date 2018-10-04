#!/bin/sh
CURRENT_DIR="$(cd "$(dirname "${0}")" && pwd)"

set -x

COMPOSE_FILE="${1:-docker-compose.yml}"
COMPOSE_FILE="${CURRENT_DIR}/${COMPOSE_FILE}"

cd "${CURRENT_DIR}"
SECS="3"
while :; do
    if [ -f ./.env ]; then
        . ./.env
        if [ -z "${MAILGUN_DOMAIN}" ]; then
            printf "%s\\n" "MAILGUN_DOMAIN variable isn't set in $(realpath ./.env), exiting ..." >&2
            exit 1
        elif [ -z "${MAILGUN_API}" ]; then
            printf "%s\\n" "MAILGUN_API variable isn't set in $(realpath ./.env), exiting ..." >&2
            exit 1
        fi
    else
        printf "%s\\n" "$(realpath ./.env) file doesn't exists, exiting ..." >&2
        exit 1
    fi
    docker-compose -f "${COMPOSE_FILE}" build && \
    docker-compose -f "${COMPOSE_FILE}" up
    printf "%s\\n" "respawing in ${SECS} secs ..."
    sleep "${SECS}"
done
