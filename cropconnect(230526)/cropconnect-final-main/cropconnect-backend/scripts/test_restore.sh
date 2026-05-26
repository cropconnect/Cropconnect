#!/usr/bin/env bash
set -euo pipefail

# Restores a fresh backup into an isolated test DB so backups are proven usable.
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
test_db="cropconnect_restore_test"

required_vars=(MYSQL_HOST MYSQL_PORT MYSQL_USER MYSQL_PASSWORD MYSQL_DATABASE)
for var_name in "${required_vars[@]}"; do
  if [[ -z "${!var_name:-}" ]]; then
    echo "RESTORE FAILED: Missing required environment variable: ${var_name}" >&2
    exit 1
  fi
done

cleanup() {
  MYSQL_PWD="${MYSQL_PASSWORD}" mysql \
    --host="${MYSQL_HOST}" \
    --port="${MYSQL_PORT}" \
    --user="${MYSQL_USER}" \
    --execute="DROP DATABASE IF EXISTS \`${test_db}\`;" >/dev/null 2>&1 || true
}
trap cleanup EXIT

if ! output="$("${script_dir}/backup_db.sh" 2>&1)"; then
  echo "RESTORE FAILED: ${output}" >&2
  exit 1
fi

backup_file="$(printf '%s\n' "${output}" | awk '/Backup written to / {print $4}' | tail -n 1)"
if [[ -z "${backup_file}" || ! -f "${backup_file}" ]]; then
  echo "RESTORE FAILED: backup file was not created" >&2
  exit 1
fi

if ! MYSQL_PWD="${MYSQL_PASSWORD}" mysql \
  --host="${MYSQL_HOST}" \
  --port="${MYSQL_PORT}" \
  --user="${MYSQL_USER}" \
  --execute="DROP DATABASE IF EXISTS \`${test_db}\`; CREATE DATABASE \`${test_db}\`;"; then
  echo "RESTORE FAILED: could not create ${test_db}" >&2
  exit 1
fi

if ! gunzip < "${backup_file}" | MYSQL_PWD="${MYSQL_PASSWORD}" mysql \
  --host="${MYSQL_HOST}" \
  --port="${MYSQL_PORT}" \
  --user="${MYSQL_USER}" \
  "${test_db}"; then
  echo "RESTORE FAILED: restore import failed" >&2
  exit 1
fi

if ! MYSQL_PWD="${MYSQL_PASSWORD}" mysql \
  --host="${MYSQL_HOST}" \
  --port="${MYSQL_PORT}" \
  --user="${MYSQL_USER}" \
  --database="${test_db}" \
  --execute="SELECT COUNT(*) FROM users;" >/dev/null; then
  echo "RESTORE FAILED: users table check failed" >&2
  exit 1
fi

echo "RESTORE OK"
