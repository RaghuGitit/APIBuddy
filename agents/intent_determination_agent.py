from langchain_core.prompts import ChatPromptTemplate
from config.llm import get_llm
from state.apibuddy_state import APIBuddyState
from pydantic import BaseModel, Field
from typing import Literal

model = get_llm()

PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are an intent classification agent for an API platform.\n"
     "Classify the user request into exactly one of the following intents:\n"
     "- SCHEMA_THEN_API: User wants to define a data schema then generate API\n"
     "- API_ONLY: User wants to generate API without explicit schema\n"
     "- EXTRACT_SCHEMAS_ONLY: User wants to extract schemas from an API spec\n"
     "- COMPARE_API_SPECS: User wants to compare old and new API specifications for compatibility\n"
     "- INVALID: User request is unclear, unrelated, or cannot be classified\n"
     "Respond with ONLY the intent and confidence score."),
    ("human", "{goal}")
])

# Create a Pydantic model for structured output from the model
class IntentSchema(BaseModel):
    intent: Literal["SCHEMA_THEN_API", "API_ONLY", "EXTRACT_SCHEMAS_ONLY", "COMPARE_API_SPECS", "INVALID"] = Field(description='Intent of the user')
    intent_confidence: float = Field(description='Confidence score of the intent classification between 0 and 1')

structured_model = model.with_structured_output(IntentSchema)

def intent_determination_agent(state: APIBuddyState) -> APIBuddyState:
    response = structured_model.invoke(
        PROMPT.format_messages(goal=state["user_goal"])
    )

    intent = response.intent
    intent_confidence = response.intent_confidence
    
    # Clamp confidence for safety
    intent_confidence = max(0.0, min(intent_confidence, 1.0))

    print(f"Determined intent: {intent}")
    print(f"Intent Confidence: {intent_confidence:.2f}")

    if intent not in ("SCHEMA_THEN_API", "API_ONLY", "EXTRACT_SCHEMAS_ONLY","COMPARE_API_SPECS","INVALID"):
        raise ValueError("Invalid intent classification")

    if intent == "INVALID":
        print("Warning: User Request is classified as INVALID")
        state["task_log"].append("Intent classification: INVALID - request unclear or unrelated")
    else:
        state["intent"] = intent
        state["intent_confidence"] = intent_confidence
        state["task_log"].append(f"Intent determined: {intent}")
        state["task_log"].append(f"Intent confidence: {intent_confidence:.2f}")

    return state
