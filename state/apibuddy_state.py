from typing import TypedDict, Optional, Dict, Any, List, Literal

class APIBuddyState(TypedDict):
    # User intent
    user_goal: str

    # Intent classification
    # intent: Literal[
    #     "SCHEMA_THEN_API",
    #     "API_ONLY"
    # ]

    # Keeping intent as str instead of literal since intent_determination_agent output 
    # is a structured output
    intent: str
    intent_confidence: float

    # JSON schema
    json_schema: Optional[Dict[str, Any]]
    schema_explanation: Optional[str]
    schema_name: Optional[str]

    # API Specification
    api_spec: Optional[Dict[str, Any]]
    linked_components: Optional[List[str]]

    # Governance
    requires_approval: bool
    approval_status: Optional[str]  # APPROVED | REJECTED

    # Audit
    task_log: List[str]
