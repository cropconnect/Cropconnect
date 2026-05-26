# Public and authenticated request rate-limit helpers.
import time

from fastapi import HTTPException, Request

from config import settings
from db.connections import get_connection
from logging_config import configure_logging

logger = configure_logging()
PUBLIC_RATE_LIMITS: dict[str, list[float]] = {}
AI_RATE_LIMITS: dict[str, list[float]] = {}
PUBLIC_RATE_LIMIT_DB_FAIL_OPEN = settings.public_rate_limit_db_fail_open


def public_client_host(request: Request) -> str:
    # Set TRUST_PROXY_HEADERS=true on Railway — proxy sits in front of all services
    forwarded_for = request.headers.get("x-forwarded-for", "").split(",", 1)[0].strip()
    if settings.trust_proxy_headers and forwarded_for:
        return forwarded_for[:255]
    return (request.client.host if request.client else "unknown")[:255]


def rate_limit_public_request(request: Request, bucket: str, limit: int, window_seconds: int) -> None:
    rate_limit_named_key(bucket, public_client_host(request), limit, window_seconds)


def rate_limit_authenticated_request(owner_id: int, bucket: str, limit: int, window_seconds: int) -> None:
    rate_limit_named_key(bucket, f"user:{owner_id}", limit, window_seconds)


def rate_limit_ai_request(request: Request, user_id: int | None = None, now: float | None = None) -> None:
    """Apply per-user AI sliding-window limits before expensive model calls."""
    identity = f"user:{user_id}" if user_id is not None else f"ip:{public_client_host(request)}"
    retry_after = _check_sliding_windows(
        bucket="ai",
        identity=identity,
        limits=((10, 60), (50, 60 * 60)),
        now=now,
    )
    if retry_after > 0:
        # Return Retry-After so clients know exactly when an AI request can be retried.
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Try again in {retry_after} seconds.",
            headers={"Retry-After": str(retry_after)},
        )


def _check_sliding_windows(
    bucket: str,
    identity: str,
    limits: tuple[tuple[int, int], ...],
    now: float | None = None,
) -> int:
    global AI_RATE_LIMITS
    current_time = now if now is not None else time.time()
    longest_window = max(window_seconds for _limit, window_seconds in limits)
    key = f"{bucket}:{identity}"[:255]
    timestamps = [
        timestamp
        for timestamp in AI_RATE_LIMITS.get(key, [])
        if current_time - timestamp < longest_window
    ]
    retry_after = 0
    for limit, window_seconds in limits:
        recent = [timestamp for timestamp in timestamps if current_time - timestamp < window_seconds]
        if len(recent) >= limit:
            oldest = min(recent)
            retry_after = max(retry_after, int((oldest + window_seconds) - current_time) + 1)
    if retry_after:
        AI_RATE_LIMITS[key] = timestamps
        return retry_after
    timestamps.append(current_time)
    AI_RATE_LIMITS[key] = timestamps
    return 0


def rate_limit_named_key(bucket: str, client_key: str, limit: int, window_seconds: int) -> None:
    global PUBLIC_RATE_LIMITS
    client_host = str(client_key or "unknown")[:255]
    try:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(
                    "DELETE FROM public_rate_limits WHERE requested_at < DATE_SUB(UTC_TIMESTAMP(), INTERVAL %s SECOND)",
                    (window_seconds,),
                )
                cursor.execute(
                    """
                    SELECT COUNT(*) AS count
                    FROM public_rate_limits
                    WHERE bucket = %s
                      AND client_host = %s
                      AND requested_at >= DATE_SUB(UTC_TIMESTAMP(), INTERVAL %s SECOND)
                    """,
                    (bucket, client_host, window_seconds),
                )
                row = cursor.fetchone() or {}
                if int(row.get("count") or 0) >= limit:
                    raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")
                cursor.execute(
                    "INSERT INTO public_rate_limits (bucket, client_host) VALUES (%s, %s)",
                    (bucket, client_host),
                )
            conn.commit()
        return
    except HTTPException:
        raise
    except Exception as exc:
        if not PUBLIC_RATE_LIMIT_DB_FAIL_OPEN:
            raise HTTPException(status_code=503, detail="Rate limiter is unavailable") from exc
        logger.exception("MySQL rate limiter unavailable, using in-memory fallback: %s", exc)

    key = f"{bucket}:{client_host}"
    # Fallback is process-local: multi-worker deployments get per-worker limits.
    logger.warning(
        "Rate limiter using in-memory fallback for key=%s - "
        "limits are per-worker in multi-process deployments",
        key,
    )
    if len(PUBLIC_RATE_LIMITS) > 50_000:
        cutoff = sorted(PUBLIC_RATE_LIMITS.keys())[10_000]
        PUBLIC_RATE_LIMITS = {k: v for k, v in PUBLIC_RATE_LIMITS.items() if k >= cutoff}
    now = time.time()
    recent = [timestamp for timestamp in PUBLIC_RATE_LIMITS.get(key, []) if now - timestamp < window_seconds]
    if len(recent) >= limit:
        raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")
    recent.append(now)
    PUBLIC_RATE_LIMITS[key] = recent
