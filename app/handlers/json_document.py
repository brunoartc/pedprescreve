"""Handler for JSON document operations"""

import json
import logging
from http import HTTPStatus

from app.infra.dynamo.json_document.create_json_document import (
    insert_json_document,
    update_json_document,
)
from app.infra.dynamo.json_document.delete_json_document import delete_json_document_by_id
from app.infra.dynamo.json_document.get_json_document import (
    get_all_json_documents,
    get_json_document_by_id,
)
from app.interfaces.api_gateway import (
    ApiGatewayHttpException,
    ApiGatewayResponse,
    handle_api_gateway_cors,
    handle_api_gateway_errors,
)
from app.interfaces.json_document import JsonDocument

logger = logging.getLogger(__name__)


@handle_api_gateway_errors
def handle_get_json_document(event: dict, _context: dict):
    """Handle API request to retrieve JSON documents."""

    query = event.get("queryStringParameters", {}) or {}
    document_id = str(query.get("json_document_id", ""))

    if not document_id:
        last_key_raw = query.get("lastEvaluatedKey")
        last_key = json.loads(last_key_raw) if last_key_raw else None
        documents, evaluated_key = get_all_json_documents(last_evaluated_key=last_key)

        return ApiGatewayResponse(
            statusCode=HTTPStatus.OK,
            body={
                "response": [item.__dict__ for item in documents],
                "lastEvaluatedKey": evaluated_key,
            },
        )

    result = get_json_document_by_id(document_id)
    if not result:
        raise ValueError(f"JSON document with id {document_id} not found")

    return ApiGatewayResponse(statusCode=HTTPStatus.OK, body={"response": result.__dict__})


@handle_api_gateway_errors
def handle_create_json_document(event: dict, _context):
    """Handle API request to create a JSON document."""

    body_json = json.loads(event["body"])
    new_document = JsonDocument(**body_json)

    if not new_document.title or not new_document.title.strip():
        raise ApiGatewayHttpException(
            status_code=HTTPStatus.BAD_REQUEST,
            message="JSON document title is required and cannot be empty.",
        )

    if not isinstance(new_document.payload, dict):
        raise ApiGatewayHttpException(
            status_code=HTTPStatus.BAD_REQUEST,
            message="JSON document payload must be an object.",
        )

    insert_json_document(new_document)

    return ApiGatewayResponse(
        statusCode=HTTPStatus.OK,
        body={
            "message": "JSON document created successfully",
            "result": new_document.__dict__,
        },
    )


@handle_api_gateway_errors
@handle_api_gateway_cors
def handle_update_json_document(event: dict, _context):
    """Handle API request to update a JSON document."""

    body_json = json.loads(event["body"])

    if not body_json.get("id") or not str(body_json.get("id", "")).strip():
        raise ApiGatewayHttpException(
            status_code=HTTPStatus.BAD_REQUEST,
            message="JSON document id is required for update.",
        )

    existing_document = get_json_document_by_id(str(body_json["id"]))
    if not existing_document:
        raise ValueError(f"JSON document with id {body_json['id']} not found")

    json_document = JsonDocument(**body_json)

    if not json_document.title or not json_document.title.strip():
        raise ApiGatewayHttpException(
            status_code=HTTPStatus.BAD_REQUEST,
            message="JSON document title is required and cannot be empty.",
        )

    if not isinstance(json_document.payload, dict):
        raise ApiGatewayHttpException(
            status_code=HTTPStatus.BAD_REQUEST,
            message="JSON document payload must be an object.",
        )

    json_document.created_at = existing_document.created_at
    json_document.update_timestamp()
    update_json_document(json_document)

    return ApiGatewayResponse(
        statusCode=HTTPStatus.OK,
        body={
            "message": "JSON document updated successfully",
            "result": json_document.__dict__,
        },
    )


@handle_api_gateway_errors
@handle_api_gateway_cors
def handle_delete_json_document(event: dict, _context):
    """Handle API request to delete a JSON document."""

    query = event.get("queryStringParameters", {}) or {}
    document_id = str(query.get("json_document_id", ""))

    if not document_id:
        raise ValueError("Missing parameter json_document_id")

    delete_json_document_by_id(document_id)

    return ApiGatewayResponse(
        statusCode=HTTPStatus.NO_CONTENT,
        body={"message": f"JSON document {document_id} deleted successfully"},
    )
