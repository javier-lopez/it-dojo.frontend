#!/bin/bash
CURRENT_DIR="$(cd "$(dirname "${0}")" && pwd)"

set -x

COMPOSE_FILE="${1:-docker-compose-werkzeug.yml}"
COMPOSE_FILE="${CURRENT_DIR}/${COMPOSE_FILE}"

clean_compose(){
    docker-compose -f "${COMPOSE_FILE}" rm -f && \
    sudo find .  -maxdepth 2 -iname "__pycache__" -exec rm -fr {} \; && \
    docker images |grep -i none | awk '{print $3}' | xargs -I{} docker rmi -f {} 2>&- || \
    docker-compose -f "${COMPOSE_FILE}" rm -f && \
    sudo find .  -maxdepth 2 -iname "__pycache__" -exec rm -fr {} \; && \
    docker images |grep -i none | awk '{print $3}' | xargs -I{} docker rmi -f {} 2>&-
}

cd "${CURRENT_DIR}"
SECS="3"
while :; do
    if [ -f ./.env ]; then
        . ./.env
        if [ -z "${MAILGUN_API}" ]; then
            printf "%s\\n" "MAILGUN_API variable isn't set in $(realpath ./.env), exiting ..." >&2
            exit 1
        fi
    else
        printf "%s\\n" "$(realpath ./.env) file doesn't exists, exiting ..." >&2
        exit 1
    fi
    clean_compose
    docker-compose -f "${COMPOSE_FILE}" build && \
    docker-compose -f "${COMPOSE_FILE}" up
    printf "%s\\n" "respawing in ${SECS} secs ..."
    sleep "${SECS}"
done
