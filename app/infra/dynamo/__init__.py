"""Dynamo utility helpers"""

from dataclasses import asdict
from datetime import datetime
from decimal import Decimal


def _serialize_value(value):
    serialized = value

    if isinstance(value, datetime):
        serialized = int(value.timestamp())
    elif isinstance(value, bool):
        serialized = value
    elif isinstance(value, float):
        serialized = Decimal(str(value))
    elif isinstance(value, int):
        serialized = Decimal(value)
    elif isinstance(value, dict):
        serialized = {key: _serialize_value(val) for key, val in value.items()}
    elif isinstance(value, list):
        serialized = [_serialize_value(val) for val in value]

    return serialized


def generate_update_expression(update_fields: dict) -> tuple:
    """Generate DynamoDB update expression and attributes"""

    update_expression = "SET "
    update_expression += ", ".join([f"#{key} = :{key}" for key in update_fields])
    expression_attribute_values = {f":{key}": value for key, value in update_fields.items()}
    expression_attribute_names = {f"#{key}": key for key in update_fields}

    return update_expression, expression_attribute_values, expression_attribute_names


def filter_update_fields(
    model_obj: object,
    filter_fields: list = None,
    not_in: bool = False,
) -> dict:
    """Filter object fields before update"""

    model_dict = asdict(model_obj)
    model_dict = _serialize_value(model_dict)

    if not filter_fields:
        return model_dict

    if not_in:
        return {key: val for key, val in model_dict.items() if key not in filter_fields}

    return {key: val for key, val in model_dict.items() if key in filter_fields}
