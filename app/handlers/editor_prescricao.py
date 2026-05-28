"""Handler to serve the local prescription editor HTML."""

from http import HTTPStatus
from pathlib import Path


_EDITOR_HTML_PATH = Path(__file__).resolve().parents[2] / "editor_prescricao.html"


def _build_headers(origin: str | None) -> dict[str, str]:
    """Build response headers for HTML and basic CORS support."""

    allow_origin = origin if origin else "*"
    return {
        "Content-Type": "text/html; charset=utf-8",
        "Access-Control-Allow-Origin": allow_origin,
        "Access-Control-Allow-Headers": (
            "Content-Type,X-Amz-Date,Authorization,"
            "X-Api-Key,X-Amz-Security-Token"
        ),
        "Access-Control-Allow-Methods": "GET,OPTIONS",
    }


def handle_editor_prescricao(event: dict, _context: dict) -> dict[str, object]:
    """Serve the HTML prescription editor without any database integration."""

    headers = event.get("headers", {}) or {}
    origin = headers.get("origin") or headers.get("Origin")

    if event.get("httpMethod") == "OPTIONS":
        return {
            "isBase64Encoded": False,
            "statusCode": HTTPStatus.OK,
            "headers": _build_headers(origin),
            "body": "",
        }

    if not _EDITOR_HTML_PATH.exists():
        return {
            "isBase64Encoded": False,
            "statusCode": HTTPStatus.INTERNAL_SERVER_ERROR,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": origin if origin else "*",
            },
            "body": '{"message":"editor_prescricao.html not found"}',
        }

    return {
        "isBase64Encoded": False,
        "statusCode": HTTPStatus.OK,
        "headers": _build_headers(origin),
        "body": _EDITOR_HTML_PATH.read_text(encoding="utf-8"),
    }