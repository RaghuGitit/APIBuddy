from langgraph.graph import StateGraph, END
from state.apibuddy_state import APIBuddyState
from agents.intent_determination_agent import intent_determination_agent
from agents.json_schema_agent import json_schema_agent
from agents.apispec_linking_agent import api_spec_linking_agent
from agents.apispec_authoring_agent import apispec_authoring_agent
from supervisor.supervisor_agent import supervisor_agent

def route_after_intent(state: APIBuddyState) -> str:
    if state["intent"] == "SCHEMA_THEN_API":
        return "json_schema_agent"
    return "api_spec_authoring_agent"

def build_workflow():
    graph = StateGraph(APIBuddyState)

    graph.add_node("intent_determination_agent", intent_determination_agent)
    graph.add_node("json_schema_agent", json_schema_agent)
    graph.add_node("api_spec_linking_agent", api_spec_linking_agent)
    graph.add_node("api_spec_authoring_agent", apispec_authoring_agent)
    graph.add_node("supervisor", supervisor_agent)

    # Entry
    graph.set_entry_point("intent_determination_agent")

    # Intent-based routing
    graph.add_conditional_edges(
        "intent_determination_agent",
        route_after_intent,
        {
            "json_schema_agent": "json_schema_agent",
            "api_spec_authoring_agent": "api_spec_authoring_agent"
        }
    )
    # Schema-first path
    graph.add_edge("json_schema_agent", "api_spec_linking_agent")
    graph.add_edge("api_spec_linking_agent", "supervisor")

    # API-only path
    graph.add_edge("api_spec_authoring_agent", "supervisor")

    # End
    graph.add_edge("supervisor", END)

    return graph.compile()
