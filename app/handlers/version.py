"""Version endpoint handler"""

import os
from http import HTTPStatus

from app.interfaces.api_gateway import ApiGatewayResponse


def version_handler(event, _context):
    """Return service version"""

    return ApiGatewayResponse(
        statusCode=HTTPStatus.OK,
        body={"response": {"version": os.getenv("version", "unknown")}},
    ).generate_response(origin=event.get("headers", {}).get("origin", "No origin header"))
