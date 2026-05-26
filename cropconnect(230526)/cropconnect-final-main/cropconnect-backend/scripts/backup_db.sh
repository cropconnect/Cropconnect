#!/usr/bin/env bash
set -euo pipefail

# Schedule daily via Railway cron. Test a full restore before going live.

required_vars=(MYSQL_HOST MYSQL_PORT MYSQL_USER MYSQL_PASSWORD MYSQL_DATABASE)
for var_name in "${required_vars[@]}"; do
  if [[ -z "${!var_name:-}" ]]; then
    echo "Missing required environment variable: ${var_name}" >&2
    exit 1
  fi
done

backup_dir="/backups"
timestamp="$(date +%Y%m%d_%H%M%S)"
backup_file="${backup_dir}/cropconnect_${timestamp}.sql.gz"

mkdir -p "${backup_dir}"

MYSQL_PWD="${MYSQL_PASSWORD}" mysqldump \
  --host="${MYSQL_HOST}" \
  --port="${MYSQL_PORT}" \
  --user="${MYSQL_USER}" \
  --single-transaction \
  --routines \
  --triggers \
  "${MYSQL_DATABASE}" | gzip > "${backup_file}"

find "${backup_dir}" -maxdepth 1 -name "cropconnect_*.sql.gz" -type f -mtime +7 -delete

echo "Backup written to ${backup_file}"
