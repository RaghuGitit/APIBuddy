from state.apibuddy_state import APIBuddyState

def apispec_authoring_agent(state: APIBuddyState) -> APIBuddyState:
    """
    Direct API spec creation without schema-first approach.
    """
    openapi_spec = {
        "openapi": "3.0.3",
        "info": {
            "title": "API Spec Created Directly",
            "version": "1.0.0"
        },
        "paths": {
            "/example": {
                "get": {
                    "summary": "Example endpoint",
                    "responses": {
                        "200": {"description": "OK"}
                    }
                }
            }
        }
    }

    state["api_spec"] = openapi_spec
    state["task_log"].append("API Spec Authoring Agent executed")

    return state
