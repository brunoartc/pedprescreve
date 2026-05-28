"""API Gateway response helpers"""
from dataclasses import dataclass, field, asdict, is_dataclass
from datetime import datetime
from enum import Enum, StrEnum
from http import HTTPStatus
from typing import Any, Callable

import simplejson as json


class MimeTypes(StrEnum):
    """MIME types"""

    JSON = "application/json"


class ApiGatewayHttpException(Exception):
    """API Gateway HTTP exception"""

    def __init__(self, status_code: HTTPStatus, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"HTTP {status_code}: {message}")


class HeaderTypes(StrEnum):
    """Default header types"""

    CONTENTTYPE = "Content-Type"
    CORSALLOWORIGIN = "Access-Control-Allow-Origin"
    CORSALLOWHEADERS = "Access-Control-Allow-Headers"
    CORSALLOWMETHODS = "Access-Control-Allow-Methods"
    CORSALLOWCREDENTIALS = "Access-Control-Allow-Credentials"


@dataclass
class ApiGatewayResponse:
    """AWS API Gateway response wrapper"""

    isBase64Encoded: bool = False  # pylint: disable=invalid-name
    statusCode: int = 200  # pylint: disable=invalid-name
    headers: dict[str, str] = field(
        default_factory=lambda: {
            HeaderTypes.CONTENTTYPE: MimeTypes.JSON,
            HeaderTypes.CORSALLOWORIGIN: "*",
            HeaderTypes.CORSALLOWHEADERS: (
                "Content-Type,X-Amz-Date,Authorization,"
                "X-Api-Key,X-Amz-Security-Token"
            ),
            HeaderTypes.CORSALLOWMETHODS: "*",
        }
    )
    body: dict | str = field(default_factory=dict)

    def __post_init__(self):
        if isinstance(self.body, str):
            self.body = {"response": self.body}

    def add_header(self, header_type: HeaderTypes, header_value: str | bool):
        """Add a header to response"""
        self.headers[header_type] = header_value
        return self.__dict__

    def generate_response(self, origin: str | None = None):
        """Generate API Gateway output object"""

        if origin:
            self.add_header(HeaderTypes.CORSALLOWCREDENTIALS, True)
            self.add_header(HeaderTypes.CORSALLOWORIGIN, origin)

        def _json_default(obj: Any):
            if isinstance(obj, datetime):
                return int(obj.timestamp())
            if isinstance(obj, Enum):
                return obj.value
            if is_dataclass(obj):
                return asdict(obj)
            return obj.__dict__

        if not isinstance(self.body, (list, dict)):
            self.body = json.dumps(self.body.__dict__, default=_json_default, use_decimal=True)
        else:
            self.body = json.dumps(self.body, default=_json_default, use_decimal=True)

        return self.__dict__


def handle_api_gateway_errors(
    func: Callable[[dict, dict], ApiGatewayResponse | dict[str, object]],
) -> Callable[[dict, dict], dict[str, object]]:
    """Handle common API errors and normalize response"""

    def wrapper(event: dict, _context: dict) -> dict[str, object]:
        try:
            func_return = func(event, _context)
        except ApiGatewayHttpException as err:
            api_response = ApiGatewayResponse(
                statusCode=err.status_code,
                body={"message": err.message},
            )
            return api_response.generate_response(
                origin=event.get("headers", {}).get("origin", "No origin header")
            )
        except ValueError as err:
            return ApiGatewayResponse(
                statusCode=HTTPStatus.BAD_REQUEST,
                body=f"ValueError({str(err)})",
            ).generate_response(origin=event.get("headers", {}).get("origin", "No origin header"))

        if isinstance(func_return, ApiGatewayResponse):
            return func_return.generate_response(
                origin=event.get("headers", {}).get("origin", "No origin header")
            )

        return func_return

    return wrapper


def handle_api_gateway_cors(
    func: Callable[[Any, Any], ApiGatewayResponse | dict[str, object]],
) -> Callable[[dict, dict], dict[str, object]]:
    """Handle CORS preflight requests"""

    def wrapper(event: dict, _context: dict) -> dict[str, object]:
        if event.get("httpMethod") == "OPTIONS":
            api_response = ApiGatewayResponse(statusCode=HTTPStatus.OK, body="")
            api_response.add_header(
                HeaderTypes.CORSALLOWMETHODS,
                "GET,POST,PUT,PATCH,DELETE,OPTIONS",
            )
            return api_response.generate_response(
                origin=event.get("headers", {}).get("origin", "No origin header")
            )

        func_return = func(event, _context)
        if isinstance(func_return, ApiGatewayResponse):
            return func_return.generate_response(
                origin=event.get("headers", {}).get("origin", "No origin header")
            )

        return func_return

    return wrapper
