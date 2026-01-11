import os
import json
import yaml
from typing import Dict, Any


def api_spec_loader(file_path: str) -> Dict[str, Any]:
    """
    Load an OpenAPI specification from JSON or YAML file.
    """

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"API spec file not found: {file_path}")

    with open(file_path, "r") as f:
        if file_path.endswith(".json"):
            return json.load(f)
        elif file_path.endswith((".yaml", ".yml")):
            return yaml.safe_load(f)
        else:
            raise ValueError("Unsupported file format (use .json/.yaml/.yml)")
