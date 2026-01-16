from state.apibuddy_state import APIBuddyState
from langgraph.types import interrupt

CONFIDENCE_THRESHOLD = 0.75

def governance_gate_agent(state: APIBuddyState) -> APIBuddyState:
    state["task_log"].append("Governance Gate Agent invoked")

    if state["intent_confidence"] < CONFIDENCE_THRESHOLD:
        print("\nLOW INTENT CONFIDENCE")
        print(f"Intent: {state['intent']}")
        print(f"Confidence: {state['intent_confidence']:.2f}")

        decision = input("Proceed with this intent? (yes/no): ").strip().lower()
        if decision != "yes":
            raise RuntimeError("Execution stopped due to low confidence")

        state["task_log"].append("User confirmed low-confidence intent")

    if state["requires_approval"]:
        if (state["intent"] == "SCHEMA_THEN_API"):           
            print("\n--- HUMAN APPROVAL REQUIRED ---")
            print("Generated JSON Schema:\n")            
            print(state["json_schema"])
            print("Generated API Spec:\n")
            print(state["api_spec"])
        if (state["intent"] == "EXTRACT_SCHEMAS_ONLY"):
            print("\n--- HUMAN APPROVAL REQUIRED ---")
            print(f"Number of extracted schemas: {state.get('number_of_extracted_schema_files', 'N/A')}")
            print(f"Extracted schema files located at: {state.get('temp_schema_dir', 'N/A')}")
        if (state["intent"] == "COMPARE_API_SPECS"):
            print(f"Compatibility Status of the new API: {state.get('compatibility_status', 'N/A')}")
            print("\n--- HUMAN APPROVAL REQUIRED ---")

        # ---- Prepare Approval Payload ----
        approval_payload = {
            "action": "FINAL_APPROVAL",
            "options": ["APPROVED", "REJECTED"]
        }

        state["pending_approval"] = approval_payload
        state["approval_decision"] = None

        state["task_log"].append(
            "Final approval from the user"
        )

        # Interrupt workflow for user approval
        decision = interrupt(approval_payload)

        if decision["approved"] == "APPROVED":
            state["task_log"].append("Final Approval by user")
            print("In resume - Final Approval by user")
            return state

        if decision["approved"] == "REJECTED":
            state["task_log"].append("Final Rejection by user")
            print("In resume - Final Rejection by user")

        # decision = input("\nApprove to proceed? (yes/no): ").strip().lower()

        # if decision != "yes":
        #     state["approval_status"] = "REJECTED"
        #     raise RuntimeError("Execution stopped by User during governance approval")
        # print("Approved by User.")
        # state["approval_status"] = "APPROVED"
        # state["task_log"].append("User approved execution")

    return state
