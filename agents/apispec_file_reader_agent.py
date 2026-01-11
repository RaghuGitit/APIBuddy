from state.apibuddy_state import APIBuddyState
from loaders.api_spec_loader import api_spec_loader


def apispec_file_reader_agent(state: APIBuddyState) -> APIBuddyState:
    """
    Reads old and new API spec files from project folders
    and loads them into state.
    """

    old_path = state.get("old_api_spec_path")
    new_path = state.get("new_api_spec_path")

    if not old_path or not new_path:
        raise ValueError("Both old and new API spec paths must be provided")

    state["old_api_spec"] = api_spec_loader(old_path)
    state["new_api_spec"] = api_spec_loader(new_path)

    state["task_log"].append(
        f"Loaded old API spec from {old_path}"
    )
    state["task_log"].append(
        f"Loaded new API spec from {new_path}"
    )

    return state
