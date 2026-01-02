import json
from langchain_core.prompts import ChatPromptTemplate
from state.apibuddy_state import APIBuddyState
from config.llm import get_llm

llm = get_llm()

PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are a strict JSON Schema generator. "
     "Return ONLY valid JSON. No explanations."),
    ("human", "{goal}")
])

def json_schema_agent(state: APIBuddyState) -> APIBuddyState:
    response = llm.invoke(
        PROMPT.format_messages(goal=state["user_goal"])
    )

    state["json_schema"] = json.loads(response.content)
    state["schema_name"] = "User"
    state["schema_explanation"] = "Generated JSON schema from user goal"
    state["task_log"].append("JSON Schema Agent executed")

    return state
