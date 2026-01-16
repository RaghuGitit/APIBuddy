from langchain_core.prompts import ChatPromptTemplate
from config.llm import get_llm
from state.apibuddy_state import APIBuddyState
from pydantic import BaseModel, Field
from typing import Literal
from langgraph.types import interrupt
from config.intent_models import IntentDetectionResult
from config.intents import ALL_INTENTS

# model = get_llm()

# PROMPT = ChatPromptTemplate.from_messages([
#     ("system",
#      "You are an intent classification agent for an API platform.\n"
#      "Classify the user request into exactly one of the following intents:\n"
#      "- SCHEMA_THEN_API: User wants to define a data schema then generate API\n"
#      "- API_ONLY: User wants to generate API without explicit schema\n"
#      "- EXTRACT_SCHEMAS_ONLY: User wants to extract schemas from an API spec\n"
#      "- COMPARE_API_SPECS: User wants to compare old and new API specifications for compatibility\n"
#      "- INVALID: User request is unclear, unrelated, or cannot be classified\n"
#      "Respond with ONLY the intent and confidence score."),
#     ("human", "{goal}")
# ])

PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """
            You are an intent classification system for an API lifecycle platform.

            Your job:
            - Identify ALL applicable intents from the user request
            - Return them sorted by confidence DESC
            - Do NOT hallucinate unsupported intents

            Allowed intents:
            - SCHEMA_THEN_API
            - API_ONLY
            - EXTRACT_SCHEMAS_ONLY
            - COMPARE_API_SPECS

            Explanation of intents:
            "- SCHEMA_THEN_API: User wants to define a data schema then generate API\n"
            "- API_ONLY: User wants to generate API Specification file\n"
            "- EXTRACT_SCHEMAS_ONLY: User wants to extract schemas from an API specification\n"
            "- COMPARE_API_SPECS: User wants to compare old and new API specifications for compatibility\n"
            "- INVALID: User request is unclear, unrelated, or cannot be classified\n"
        """
    ),
    ("human", "{goal}")
])

# Create a Pydantic model for structured output from the model
# class IntentSchema(BaseModel):
#     intent: Literal["SCHEMA_THEN_API", "API_ONLY", "EXTRACT_SCHEMAS_ONLY", "COMPARE_API_SPECS", "INVALID"] = Field(description='Intent of the user')
#     intent_confidence: float = Field(description='Confidence score of the intent classification between 0 and 1')

# LLM with structured output
structured_model = get_llm().with_structured_output(IntentDetectionResult)

def intent_determination_agent(state: APIBuddyState) -> APIBuddyState:
    # response = structured_model.invoke(
    #     PROMPT.format_messages(goal=state["user_goal"])
    # )
    # Invoke LLM with structured output
    result: IntentDetectionResult = structured_model.invoke(
        PROMPT.format_messages(goal=state["user_goal"])
    )

    # Validate & normalize
    intent_candidates = []

    for item in result.intents:
        if item.intent not in ALL_INTENTS:
            continue

        intent_candidates.append({
            "intent": item.intent,
            "confidence": round(item.confidence, 2)
        })

    if not intent_candidates:
        raise RuntimeError("No valid intents detected")

    # Ensure sorted by confidence desc
    intent_candidates.sort(
        key=lambda x: x["confidence"],
        reverse=True
    )

    state["intent_candidates"] = intent_candidates
    state["current_intent_index"] = 0

    state["task_log"].append(
        f"Detected intent candidates: {intent_candidates}"
    )

    # INTERRUPT: User confirms the intents
    approval_payload = {
        "action": "CONFIRM_INTENTS",
        "intent_candidates": intent_candidates,
        "instruction": "Select one or more intents to execute in order"
    }

    state["pending_approval"] = approval_payload
    state["approval_decision"] = None

    # Interrupt workflow for user approval
    decision = interrupt(approval_payload)

    # ---- Resume After User Decision ----
    print(f"User decision on Intents list: {decision}")

    if decision["approved"] == "APPROVED":
        state["task_log"].append(
        f"User selected intents: {intent_candidates}")
        # state["selected_intents"] = intent_candidates
        state["selected_intents"] = [
            item["intent"] for item in intent_candidates
        ]
        print("In resume - User approved the intents list")
        return state

    if decision["approved"] == "REJECTED":
        print("In resume - User rejected the intents list")
        state["task_log"].append("User rejected the intents list")
        # raise RuntimeError("JSON Schema rejected by user")
        return state

    # Resume after user decision    
    # selected_intents = state.get("approval_decision")

    # if not isinstance(selected_intents, list) or not selected_intents:
    #     raise RuntimeError("No intents selected by user")

    # state["selected_intents"] = selected_intents

    # state["task_log"].append(
    #     f"User selected intents: {selected_intents}"
    # )

    return state
