import json
import tempfile
import os
from state.apibuddy_state import APIBuddyState


def schema_extraction_agent(state: APIBuddyState) -> APIBuddyState:
    """
    Extracts all schema components from an uploaded OpenAPI spec
    and stores them as individual JSON files in a temporary directory.
    """

    api_spec = state.get("api_spec")
    if not api_spec:
        raise ValueError("No uploaded API specification found")

    components = api_spec.get("components", {})
    schemas = components.get("schemas", {})

    if not schemas:
        state["task_log"].append("No schemas found in API spec")
        state["extracted_schema_files"] = []
        return state

    # Create temp directory in project root (optional)
    temp_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "filesrepo", "temp_schemas")
    os.makedirs(temp_dir, exist_ok=True)

    # Create temp directory
    # temp_dir = tempfile.mkdtemp(prefix="apibuddy_schemas_")

    extracted_files = []

    for schema_name, schema_def in schemas.items():
        file_path = os.path.join(temp_dir, f"{schema_name}.json")

        with open(file_path, "w") as f:
            json.dump(schema_def, f, indent=2)

        extracted_files.append(file_path)

    state["temp_schema_dir"] = temp_dir
    state["extracted_schema_files"] = extracted_files
    state["number_of_extracted_schema_files"] = len(extracted_files)
    state["task_log"].append(
        f"Extracted {len(extracted_files)} schema components to {temp_dir}"
    )

    return state
