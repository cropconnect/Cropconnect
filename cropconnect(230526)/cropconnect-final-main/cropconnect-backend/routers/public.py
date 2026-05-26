from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from db.connections import get_connection
from models import EnquiryIn
from services.email_service import send_enquiry_email, smtp_configured
from services.rate_limit import rate_limit_public_request

router = APIRouter()


def raise_public_error(status_code: int, detail: str, _context: str, exc: Exception) -> None:
    raise HTTPException(status_code=status_code, detail=detail) from exc


def database_health_status():
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        return {"status": "ok", "db": "ok"}
    except Exception:
        return JSONResponse(status_code=503, content={"status": "degraded", "db": "error"})


@router.get("/health")
def health():
    return database_health_status()


@router.get("/api/health")
def api_health():
    return database_health_status()


@router.get("/")
def root():
    return {
        "service": "CropConnect ESP32 Ingestion API",
        "docs": "/docs",
        "health": "/api/health",
        "esp32_relay_command": "/api/esp32/relay-command",
        "hardware_flow": "Main ESP32 uses SIM800L to ingest sensors and poll pump commands, then forwards commands to the pump ESP32.",
    }


@router.post("/api/enquiries")
def enquiries(payload: EnquiryIn, request: Request):
    rate_limit_public_request(request, "enquiries", limit=5, window_seconds=300)
    email_sent = False
    if smtp_configured():
        try:
            send_enquiry_email(payload)
            email_sent = True
        except Exception as exc:
            raise_public_error(502, "Email delivery failed", "Enquiry email delivery failed", exc)

    return {
        "ok": True,
        "message": "Enquiry received",
        "email_sent": email_sent,
        "received_at": datetime.now(timezone.utc).isoformat(),
    }
