"""Delete JSON documents"""

import os

from app.infra.dynamo.helper import dynamodb

# Reference to DynamoDB table
table_json_documents = dynamodb.Table(os.environ["TABLE_JSON_DOCUMENTS"])  # type: ignore


def delete_json_document_by_id(document_id: str):
    """Delete a JSON document by ID."""

    key_filter = {"id": document_id}
    return table_json_documents.delete_item(Key=key_filter)
