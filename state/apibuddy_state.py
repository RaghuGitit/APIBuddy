from typing import TypedDict, Optional, Dict, Any, List, Literal

class APIBuddyState(TypedDict):
    # User intent
    user_goal: str

    # ---- Multi-candidate intent detection ----
    intent_candidates: List[Dict[str, Any]]  # [{intent, confidence}]
    selected_intents: Optional[List[str]]    # user-approved intents

    # ---- Execution pointer ----
    current_intent_index: int
    
    next_intent: Optional[str]

    # Intent classification
    # intent: Literal[
    #     "SCHEMA_THEN_API",
    #     "API_ONLY"
    # ]
    # Keeping intent as str instead of literal since intent_determination_agent output 
    # is a structured output
    intent: str
    intent_confidence: float

    # File paths
    old_api_spec_path: str
    new_api_spec_path: str

    # Loaded specs
    old_api_spec: Optional[Dict[str, Any]]
    new_api_spec: Optional[Dict[str, Any]]

    # Compatibility result
    compatibility_status: Optional[Literal[
        "BACKWARD_COMPATIBLE",
        "BREAKING"
    ]]
    compatibility_issues: Optional[List[str]]
    compatibility_report: Optional[str]

     # HITL
    pending_approval: Optional[Dict[str, Any]]
    approval_decision: Optional[Literal["APPROVED", "REJECTED"]]

    # File input
    api_spec_dir: Optional[str]      # directory path
    api_spec_file: Optional[str]     # filename
    uploaded_api_spec: Optional[Dict[str, Any]]

    # Extracted schemas
    extracted_schema_files: Optional[List[str]]
    number_of_extracted_schema_files: Optional[int]
    temp_schema_dir: Optional[str]

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
    
    # Interrupts
    # interrupt: Optional[List[Any]]
