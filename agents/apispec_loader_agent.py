import os
import json
import yaml
from state.apibuddy_state import APIBuddyState


def apispec_loader_agent(state: APIBuddyState) -> APIBuddyState:
    """
    Loads an OpenAPI spec file (JSON or YAML) from a given directory.
    """

    spec_dir = state.get("api_spec_dir")
    spec_file = state.get("api_spec_file")

    if not spec_dir or not spec_file:
        raise ValueError("API spec directory or file name not provided")

    file_path = os.path.join(spec_dir, spec_file)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"API spec file not found: {file_path}")

    with open(file_path, "r") as f:
        if spec_file.endswith(".json"):
            api_spec = json.load(f)
        elif spec_file.endswith((".yaml", ".yml")):
            api_spec = yaml.safe_load(f)
        else:
            raise ValueError("Unsupported API spec format (use .json or .yaml)")

    state["api_spec"] = api_spec
    state["task_log"].append(f"Loaded API spec from {file_path}")

    return state
