"""Create JSON documents"""

import os

from app.infra.dynamo import filter_update_fields, generate_update_expression
from app.infra.dynamo.helper import dynamodb
from app.interfaces.json_document import JsonDocument

# Reference to DynamoDB table
table_json_documents = dynamodb.Table(os.environ["TABLE_JSON_DOCUMENTS"])  # type: ignore


def insert_json_document(json_document: JsonDocument):
    """Insert or update a JSON document in the table."""

    key_filter = {"id": json_document.id}
    update_fields = filter_update_fields(json_document, list(key_filter), not_in=True)

    update_expression, expression_attribute_values, expression_attribute_names = (
        generate_update_expression(update_fields)
    )

    return table_json_documents.update_item(
        Key=key_filter,
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_attribute_values,
        ExpressionAttributeNames=expression_attribute_names,
    )


def update_json_document(json_document: JsonDocument):
    """Update an existing JSON document in the table."""

    key_filter = {"id": json_document.id}
    update_fields = filter_update_fields(json_document, list(key_filter), not_in=True)

    update_expression, expression_attribute_values, expression_attribute_names = (
        generate_update_expression(update_fields)
    )

    return table_json_documents.update_item(
        Key=key_filter,
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_attribute_values,
        ExpressionAttributeNames=expression_attribute_names,
    )
