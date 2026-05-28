"""Get JSON documents"""

import os

from app.infra.dynamo.helper import dynamodb
from app.interfaces.json_document import JsonDocument

# Reference to DynamoDB table
table_json_documents = dynamodb.Table(os.environ["TABLE_JSON_DOCUMENTS"])  # type: ignore


def get_json_document_by_id(document_id: str) -> JsonDocument | None:
    """Retrieve a JSON document by ID."""

    response = table_json_documents.get_item(Key={"id": document_id})
    if "Item" in response:
        return JsonDocument(**response["Item"])

    return None


def get_all_json_documents(
    last_evaluated_key: dict | None = None,
) -> tuple[list[JsonDocument], dict | None]:
    """Retrieve all JSON documents with pagination."""

    scan_params = {"Limit": 100}

    if last_evaluated_key:
        scan_params["ExclusiveStartKey"] = last_evaluated_key

    response = table_json_documents.scan(**scan_params)
    documents = [JsonDocument(**item) for item in response.get("Items", [])]

    last_key = response.get("LastEvaluatedKey")
    return documents, last_key
