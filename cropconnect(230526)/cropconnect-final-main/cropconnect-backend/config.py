# Centralized environment settings for the CropConnect API.
import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    mysql_public_url: str | None = None
    mysql_host: str = "127.0.0.1"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = ""
    mysql_database: str = "cropconnect"
    mysql_pool_size: int = 15
    crop_data_secret_key: str = ""
    crop_auth_token_secret: str = ""
    esp32_api_key: str = ""
    allow_global_esp32_api_key: bool = False
    contact_to_email: str = "cropconnectco@gmail.com"
    frontend_public_url: str = "https://cropconnect01.vercel.app"
    frontend_origins: str = "https://cropconnect01.vercel.app"
    public_landing_sensor_device_id: str = ""
    public_translation_enabled: bool = False
    query_api_key_enabled: bool = False
    esp32_get_write_enabled: bool = False
    public_rate_limit_db_fail_open: bool = False
    # Set TRUST_PROXY_HEADERS=true on Railway — proxy sits in front of all services
    trust_proxy_headers: bool = False
    password_reset_token_ttl_minutes: int = 30
    farm_timer_utc_offset_minutes: int = 330
    auth_cookie_secure: bool = True
    auth_cookie_samesite: str = "none"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    google_api_key: str = ""
    google_cse_id: str = ""
    data_gov_api_key: str = ""
    data_gov_market_resource_url: str = "https://api.data.gov.in/resource/current-daily-price-various-commodities-various-markets-mandi"
    market_price_limit: int = 100
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""


settings = Settings()


REQUIRED_ENV_VARS = (
    "CROP_DATA_SECRET_KEY",
    "CROP_AUTH_TOKEN_SECRET",
    "ESP32_API_KEY",
    "FRONTEND_ORIGINS",
    "MYSQL_USER",
    "MYSQL_PASSWORD",
    "MYSQL_DATABASE",
)
PLACEHOLDER_PATTERNS = ("replace-with", "your-", "changeme", "example")


def validate_required_environment() -> list[str]:
    """Return every production env problem so startup can fail with one clear message."""
    problems: list[str] = []
    values = {
        "CROP_DATA_SECRET_KEY": os.getenv("CROP_DATA_SECRET_KEY") or settings.crop_data_secret_key,
        "CROP_AUTH_TOKEN_SECRET": os.getenv("CROP_AUTH_TOKEN_SECRET") or settings.crop_auth_token_secret,
        "ESP32_API_KEY": os.getenv("ESP32_API_KEY") or settings.esp32_api_key,
        "FRONTEND_ORIGINS": os.getenv("FRONTEND_ORIGINS") or settings.frontend_origins,
        "MYSQL_HOST": os.getenv("MYSQL_HOST") or settings.mysql_host,
        "MYSQL_PUBLIC_URL": os.getenv("MYSQL_PUBLIC_URL") or settings.mysql_public_url,
        "MYSQL_USER": os.getenv("MYSQL_USER") or settings.mysql_user,
        "MYSQL_PASSWORD": os.getenv("MYSQL_PASSWORD") or settings.mysql_password,
        "MYSQL_DATABASE": os.getenv("MYSQL_DATABASE") or settings.mysql_database,
    }
    for name in REQUIRED_ENV_VARS:
        value = str(values.get(name) or "").strip()
        if not value:
            problems.append(f"{name} is missing")
            continue
        lowered = value.lower()
        if any(pattern in lowered for pattern in PLACEHOLDER_PATTERNS):
            problems.append(f"{name} uses a placeholder value")
        if name in {"CROP_DATA_SECRET_KEY", "CROP_AUTH_TOKEN_SECRET"} and len(value) < 16:
            problems.append(f"{name} must be at least 16 characters")
    if not (str(values.get("MYSQL_HOST") or "").strip() or str(values.get("MYSQL_PUBLIC_URL") or "").strip()):
        problems.append("MYSQL_HOST or MYSQL_PUBLIC_URL is required")
    return problems
