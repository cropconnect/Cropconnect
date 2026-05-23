import base64
import hashlib
import sys
from pathlib import Path
from urllib.parse import urlparse

import mysql.connector
from cryptography.fernet import Fernet, InvalidToken

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import settings  # noqa: E402
from security_crypto import ENCRYPTED_PREFIX  # noqa: E402

ENCRYPTED_PROFILE_FIELDS = ("name", "phone", "state", "location", "district", "city", "village")


def old_fernet(secret: str) -> Fernet:
    return Fernet(base64.urlsafe_b64encode(hashlib.sha256(secret.encode("utf-8")).digest()))


def new_fernet(secret: str) -> Fernet:
    dk = hashlib.pbkdf2_hmac(
        "sha256",
        secret.encode("utf-8"),
        b"cropconnect-fernet-v1",
        iterations=200_000,
    )
    return Fernet(base64.urlsafe_b64encode(dk))


def db_config() -> dict:
    if settings.mysql_public_url:
        url = urlparse(settings.mysql_public_url)
        return {
            "host": url.hostname,
            "port": int(url.port or 3306),
            "user": url.username,
            "password": url.password,
            "database": settings.mysql_database,
        }
    return {
        "host": settings.mysql_host,
        "port": settings.mysql_port,
        "user": settings.mysql_user,
        "password": settings.mysql_password,
        "database": settings.mysql_database,
    }


def decrypt_old(cipher: Fernet, value: str | None) -> str | None:
    if not value or not str(value).startswith(ENCRYPTED_PREFIX):
        return value
    token = str(value)[len(ENCRYPTED_PREFIX):]
    return cipher.decrypt(token.encode("utf-8")).decode("utf-8")


def encrypt_new(cipher: Fernet, value: str | None) -> str | None:
    if value is None:
        return None
    text = str(value)
    if not text:
        return text
    return ENCRYPTED_PREFIX + cipher.encrypt(text.encode("utf-8")).decode("utf-8")


def main() -> int:
    secret = settings.crop_data_secret_key
    if not secret:
        print("CROP_DATA_SECRET_KEY is required", file=sys.stderr)
        return 1

    old_cipher = old_fernet(secret)
    new_cipher = new_fernet(secret)
    updated = 0

    conn = mysql.connector.connect(**db_config())
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT id, name, phone, state, location, district, city, village FROM users")
            rows = cursor.fetchall() or []
            for row in rows:
                values = {}
                for field in ENCRYPTED_PROFILE_FIELDS:
                    raw_value = row.get(field)
                    if not raw_value or not str(raw_value).startswith(ENCRYPTED_PREFIX):
                        continue
                    try:
                        values[field] = encrypt_new(new_cipher, decrypt_old(old_cipher, raw_value))
                    except InvalidToken as exc:
                        raise RuntimeError(f"Could not decrypt users.id={row['id']} field={field} with old key") from exc
                if not values:
                    continue
                assignments = ", ".join(f"`{field}` = %s" for field in values)
                cursor.execute(
                    f"UPDATE users SET {assignments} WHERE id = %s",
                    tuple(values.values()) + (row["id"],),
                )
                updated += 1
        conn.commit()
    finally:
        conn.close()

    print(f"Re-encrypted profile fields for {updated} user rows.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
