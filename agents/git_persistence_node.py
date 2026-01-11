from agents.git_persistence_agent import GitPersistenceAgent
from infra.git.github_client import GitHubClient
from langgraph.errors import Interrupt
from state.apibuddy_state import APIBuddyState

# git_agent = GitPersistenceAgent(...)
github_client = GitHubClient()
git_agent = GitPersistenceAgent(github_client)

def git_persistence_node(state: APIBuddyState):

    # TODO: Add HITL approval check
    # if not state.get("approved"):
    #     raise Interrupt("Approval required before committing to Git")

    # TODO: Check the state variables and make sure these are populated in all cases
    result = git_agent.persist(
        # api_name=state["api_name"],
        # version=state["version"],
        api_name="TestAPI",
        version="0.0.1",
        openapi_spec=state.get("new_api_spec"),
        schemas=state.get("generated_schemas"),
        # change_summary=state["change_summary"]
        change_summary="From APIBuddy automated changes."
    )

    return {
        "artifacts_written": True,
        "git_branch": result["branch"],
        "pr_url": result["pr_url"]
    }
