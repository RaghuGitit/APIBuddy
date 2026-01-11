from state.apibuddy_state import APIBuddyState


def backward_compatibility_agent(state: APIBuddyState) -> APIBuddyState:
    old_spec = state.get("old_api_spec")
    new_spec = state.get("new_api_spec")

    if not old_spec or not new_spec:
        raise ValueError("Both old and new API specs must be provided")

    issues = []

    old_paths = old_spec.get("paths", {})
    new_paths = new_spec.get("paths", {})

    # Endpoint removal check
    for path, methods in old_paths.items():
        if path not in new_paths:
            issues.append(f"Endpoint removed: {path}")
            continue

        for method in methods:
            if method not in new_paths[path]:
                issues.append(f"Method removed: {method.upper()} {path}")

    # Request schema compatibility
    def extract_schema(spec, path, method):
        return (
            spec["paths"][path][method]
            .get("requestBody", {})
            .get("content", {})
            .get("application/json", {})
            .get("schema", {})
        )

    for path, methods in old_paths.items():
        for method in methods:
            if path in new_paths and method in new_paths[path]:
                old_schema = extract_schema(old_spec, path, method)
                new_schema = extract_schema(new_spec, path, method)

                old_props = old_schema.get("properties", {})
                new_props = new_schema.get("properties", {})

                old_required = set(old_schema.get("required", []))
                new_required = set(new_schema.get("required", []))

                # Removed fields
                for field in old_props:
                    if field not in new_props:
                        issues.append(
                            f"Request field removed: {field} in {method.upper()} {path}"
                        )

                # New required fields
                for field in new_required - old_required:
                    issues.append(
                        f"New required request field added: {field} in {method.upper()} {path}"
                    )

    # Response compatibility (200 only for simplicity)
    def extract_response_schema(spec, path, method):
        return (
            spec["paths"][path][method]
            .get("responses", {})
            .get("200", {})
            .get("content", {})
            .get("application/json", {})
            .get("schema", {})
        )

    for path, methods in old_paths.items():
        for method in methods:
            if path in new_paths and method in new_paths[path]:
                old_resp = extract_response_schema(old_spec, path, method)
                new_resp = extract_response_schema(new_spec, path, method)

                old_props = old_resp.get("properties", {})
                new_props = new_resp.get("properties", {})

                for field in old_props:
                    if field not in new_props:
                        issues.append(
                            f"Response field removed: {field} in {method.upper()} {path}"
                        )

    # Final decision
    if issues:
        state["compatibility_status"] = "BREAKING"
        state["compatibility_issues"] = issues
        state["compatibility_report"] = "\n".join(issues)
    else:
        state["compatibility_status"] = "BACKWARD_COMPATIBLE"
        state["compatibility_issues"] = []
        state["compatibility_report"] = "No breaking changes detected"

    state["task_log"].append(
        f"Backward compatibility check result: {state['compatibility_status']}"
    )

    return state
