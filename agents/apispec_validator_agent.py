import json
from typing import List
from openapi_spec_validator import validate_spec
from openapi_spec_validator.validation.exceptions import (
    OpenAPIValidationError,
    OpenAPISpecValidatorError,
)
from state.apibuddy_state import APIBuddyState


def _load_api_spec_from_file(path: str) -> dict:
    with open(path, "r") as f:
        if path.endswith(".json"):
            return json.load(f)
        raise ValueError("Only JSON OpenAPI specs supported in this agent")


def apispec_validator_agent(state: APIBuddyState) -> APIBuddyState:
    """
    Validates whether the provided API spec is a valid OpenAPI specification.
    """

    spec = None
    source = None

    if state.get("api_spec"):
        spec = state["api_spec"]
        source = "in-memory API spec"
    elif state.get("api_spec_file_path"):
        spec = _load_api_spec_from_file(state["api_spec_file_path"])
        source = f"file: {state['api_spec_file_path']}"
    else:
        raise ValueError("No API spec provided for validation")

    errors: List[str] = []

    try:
        validate_spec(spec)
    except OpenAPIValidationError as e:
        errors.append(str(e))
    except OpenAPISpecValidatorError as e:
        errors.append(str(e))

    if errors:
        state["api_spec_is_valid"] = False
        state["api_spec_validation_errors"] = errors
        state["task_log"].append(
            f"API Spec validation FAILED for {source}"
        )
    else:
        state["api_spec_is_valid"] = True
        state["api_spec_validation_errors"] = []
        state["task_log"].append(
            f"API Spec validation PASSED for {source}"
        )

    return state
