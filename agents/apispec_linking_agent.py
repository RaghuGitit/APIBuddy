from state.apibuddy_state import APIBuddyState

def api_spec_linking_agent(state: APIBuddyState) -> APIBuddyState:
    """
    Links generated JSON schema into OpenAPI specification
    using components/schemas references.
    """
    schema_name = state["schema_name"]
    schema = state["json_schema"]

    openapi_spec = {
        "openapi": "3.0.3",
        "info": {
            "title": "Sample API",
            "version": "1.0.0"
        },
        "paths": {
            "/users": {
                "post": {
                    "summary": "Create user",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": f"#/components/schemas/{schema_name}"
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Created"
                        }
                    }
                }
            }
        },
        "components": {
            "schemas": {
                schema_name: schema
            }
        }
    }

    state["api_spec"] = openapi_spec
    state["linked_components"] = [schema_name]
    state["task_log"].append(
        f"API Spec linked with schema '{schema_name}'"
    )

    return state
