from langchain_core.prompts import ChatPromptTemplate
from config.llm import get_llm
from state.apibuddy_state import APIBuddyState
from pydantic import BaseModel, Field
from typing import Literal

model = get_llm()

PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are an intent classification agent for an API platform.\n"
     "Classify the user request into exactly one intent:\n"
     "Respond with ONLY the intent."),
    ("human", "{goal}")
])

# Create a Pydantic model for structured output from the model
class IntentSchema(BaseModel):
    intent: Literal["SCHEMA_THEN_API", "API_ONLY"] = Field(description='Intent of the user')
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

    if intent not in ("SCHEMA_THEN_API", "API_ONLY"):
        raise ValueError("Invalid intent classification")

    state["intent"] = intent
    state["intent_confidence"] = intent_confidence
    state["task_log"].append(f"Intent determined: {intent}")
    state["task_log"].append(f"Intent confidence: {intent_confidence}")

    return state
