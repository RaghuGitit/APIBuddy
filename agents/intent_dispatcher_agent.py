from state.apibuddy_state import APIBuddyState

def intent_dispatcher_agent(state: APIBuddyState) -> str:
    idx = state["current_intent_index"]
    intents = state["selected_intents"]

    if idx >= len(intents):
        state["next_intent"] = None
        return state

    intent = intents[idx]
    state["task_log"].append(f"Dispatching intent: {intent}")

    # move pointer forward
    state["current_intent_index"] += 1
    print(f"Dispatching intent: {intent}")
    print("selected_intents:" + str(state["selected_intents"]))
    state["next_intent"] = intent 
    
    return state
