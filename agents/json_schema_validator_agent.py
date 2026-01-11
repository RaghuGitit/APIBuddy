import json
from typing import List
from jsonschema import Draft202012Validator, exceptions as jsonschema_exceptions
from state.apibuddy_state import APIBuddyState


def _load_schema_from_file(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def json_schema_validator_agent(state: APIBuddyState) -> APIBuddyState:
    """
    Validates whether the provided schema is a valid JSON Schema.
    Supports file-based or in-memory schema validation.
    """

    schema = None

    if state.get("json_schema"):
        schema = state["json_schema"]
        source = "in-memory schema"
    elif state.get("schema_file_path"):
        schema = _load_schema_from_file(state["schema_file_path"])
        source = f"file: {state['schema_file_path']}"
    else:
        raise ValueError("No JSON schema provided for validation")

    errors: List[str] = []

    try:
        print("Validating JSON Schema...")
        validator = Draft202012Validator(schema)

        for error in sorted(validator.iter_errors(schema), key=str):
            errors.append(error.message)

    except jsonschema_exceptions.SchemaError as e:
        errors.append(str(e))

    if errors:
        state["schema_is_valid"] = False
        state["schema_validation_errors"] = errors
        state["task_log"].append(
            f"JSON Schema validation FAILED for {source}"
        )
    else:
        print("JSON Schema is valid.")
        state["schema_is_valid"] = True
        state["schema_validation_errors"] = []
        state["task_log"].append(
            f"JSON Schema validation PASSED for {source}"
        )

    return state
