import json
from langchain_core.prompts import ChatPromptTemplate
from state.apibuddy_state import APIBuddyState
from config.llm import get_llm
from langgraph.types import interrupt   

llm = get_llm()

PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are a strict JSON Schema generator. "
     "Return ONLY valid JSON. No explanations."),
    ("human", "{goal}")
])

def json_schema_agent(state: APIBuddyState) -> APIBuddyState:
    """
    Generates JSON Schema and pauses workflow for user approval
    using LangGraph interrupt.
    """
    response = llm.invoke(
        PROMPT.format_messages(goal=state["user_goal"])
    )
    print("Generated JSON Schema:")
    print(response.content)
    schema = json.loads(response.content)
    state["json_schema"] = schema
    state["schema_name"] = state.get("schema_name") or "GeneratedSchema"
    state["schema_explanation"] = "Generated JSON schema from user goal"
    state["task_log"].append("JSON Schema Agent executed")

    # ---- Prepare Approval Payload ----
    approval_payload = {
        "action": "REVIEW_JSON_SCHEMA",
        "schema_name": state["schema_name"],
        "schema": schema,
        "options": ["APPROVED", "REJECTED"]
    }

    state["pending_approval"] = approval_payload
    state["approval_decision"] = None

    state["task_log"].append(
        "JSON Schema awaiting user approval"
    )

    # Interrupt workflow for user approval
    decision = interrupt(approval_payload)

    # ---- Resume After User Decision ----
    # decision = state.get("approval_decision")
    # print("approval_decision:" + str(state["approval_decision"]))

    print(f"User decision on JSON Schema agent: {decision}")

    if decision["approved"] == "APPROVED":
        state["task_log"].append("JSON Schema approved by user")
        print("In resume - JSON Schema approved by user")
        return state

    if decision["approved"] == "REJECTED":
        print("In resume - JSON Schema rejected by user")
        state["task_log"].append("JSON Schema rejected by user")
        # raise RuntimeError("JSON Schema rejected by user")
        return state

    raise RuntimeError("Invalid approval decision for JSON Schema")
