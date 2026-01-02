from state.apibuddy_state import APIBuddyState

CONFIDENCE_THRESHOLD = 0.75

def supervisor_agent(state: APIBuddyState) -> APIBuddyState:
    state["task_log"].append("Supervisor invoked")

    if state["intent_confidence"] < CONFIDENCE_THRESHOLD:
        print("\nLOW INTENT CONFIDENCE")
        print(f"Intent: {state['intent']}")
        print(f"Confidence: {state['intent_confidence']:.2f}")

        decision = input("Proceed with this intent? (yes/no): ").strip().lower()
        if decision != "yes":
            raise RuntimeError("Execution stopped due to low confidence")

        state["task_log"].append("User confirmed low-confidence intent")

    if state["requires_approval"]:
        print("\n--- HUMAN APPROVAL REQUIRED ---")
        print("Generated JSON Schema:\n")
        print(state["json_schema"])

        decision = input("\nApprove schema? (yes/no): ").strip().lower()

        if decision != "yes":
            state["approval_status"] = "REJECTED"
            raise RuntimeError("Execution stopped by Supervisor")

        state["approval_status"] = "APPROVED"
        state["task_log"].append("Supervisor approved execution")

    return state
