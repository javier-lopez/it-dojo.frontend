#!/bin/sh
CURRENT_DIR="$(cd "$(dirname "${0}")" && pwd)"

if [ -z "${1}" ]; then
    printf "%s\\n" "Define target environment: stage|pro" >&2
    exit 1
fi

cd "${CURRENT_DIR}"
cd provision/ansible/

if [ ! -f ../../.vault_pass.txt ]; then
    printf "%s\\n" "$(realpath ../../.vault_pass.txt) doesn't exists, exiting ..."
    exit 1
fi


set -x
ansible-playbook app.yml -i inventories/"${1}"/hosts -u ansible --private-key=~/.ssh/id_rsa --vault-password-file ../../.vault_pass.txt --tags api
