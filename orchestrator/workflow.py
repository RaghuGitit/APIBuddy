from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

from langgraph.graph import StateGraph, END
# from asyncio import graph
from state.apibuddy_state import APIBuddyState
from agents.intent_determination_agent import intent_determination_agent
from agents.json_schema_agent import json_schema_agent
from agents.json_schema_validator_agent import json_schema_validator_agent
from agents.apispec_linking_agent import apispec_linking_agent
from agents.apispec_authoring_agent import apispec_authoring_agent
from agents.apispec_loader_agent import apispec_loader_agent
from agents.apispec_validator_agent import apispec_validator_agent
from agents.schema_extraction_agent import schema_extraction_agent
from governance.governance_gate_agent import governance_gate_agent
from agents.apispec_file_reader_agent import apispec_file_reader_agent
from agents.backward_compatibility_agent import backward_compatibility_agent
from agents.git_persistence_node import git_persistence_node
from agents.intent_dispatcher_agent import intent_dispatcher_agent

def route_after_intent(state: APIBuddyState) -> str:
    if state["intent"] == "SCHEMA_THEN_API":
        return "json_schema_agent"
    if state["intent"] == "EXTRACT_SCHEMAS_ONLY":
        return "apispec_loader_agent"
    if state["intent"] == "COMPARE_API_SPECS":
        return "apispec_file_reader_agent"
    return "apispec_authoring_agent"

def build_workflow():
    graph = StateGraph(APIBuddyState)

    graph.add_node("intent_determination_agent", intent_determination_agent)
    graph.add_node("intent_dispatcher_agent", intent_dispatcher_agent)
    graph.add_node("json_schema_agent", json_schema_agent)
    graph.add_node("json_schema_validator_agent", json_schema_validator_agent)
    graph.add_node("apispec_linking_agent", apispec_linking_agent)
    graph.add_node("apispec_authoring_agent", apispec_authoring_agent)
    graph.add_node("apispec_loader_agent", apispec_loader_agent)
    graph.add_node("apispec_validator_agent", apispec_validator_agent)
    graph.add_node("schema_extraction_agent", schema_extraction_agent)
    graph.add_node("apispec_file_reader_agent", apispec_file_reader_agent)
    graph.add_node("backward_compatibility", backward_compatibility_agent)
    graph.add_node("governance_gate_agent", governance_gate_agent)
    graph.add_node("git_persistence_node", git_persistence_node)

    # Entry
    graph.set_entry_point("intent_determination_agent")
    graph.add_edge("intent_determination_agent", "intent_dispatcher_agent")

    # --- Conditional routing based on dispatcher return ---
    graph.add_conditional_edges(
        "intent_dispatcher_agent",
        lambda state: state["next_intent"],
        {
            "EXTRACT_SCHEMAS_ONLY": "apispec_loader_agent",
            "COMPARE_API_SPECS": "apispec_file_reader_agent",
            "SCHEMA_THEN_API": "json_schema_agent",
            None: END
        }
    )

    # Intent-based routing
    # graph.add_conditional_edges(
    #     "intent_determination_agent",
    #     route_after_intent,
    #     {
    #         "json_schema_agent": "json_schema_agent",
    #         "apispec_authoring_agent": "apispec_authoring_agent",
    #         "apispec_loader_agent": "apispec_loader_agent",
    #         "apispec_file_reader_agent": "apispec_file_reader_agent"
    #     }
    # )
    # Schema-first path
    # graph.add_edge("json_schema_agent", "json_schema_validator_agent")
    # graph.add_edge("json_schema_validator_agent", "apispec_linking_agent")
    # graph.add_edge("apispec_linking_agent", "apispec_validator_agent")
    # graph.add_edge("apispec_validator_agent", "governance_gate_agent")

    graph.add_edge("json_schema_agent", "json_schema_validator_agent")
    graph.add_edge("json_schema_validator_agent", "apispec_linking_agent")
    graph.add_edge("apispec_linking_agent", "governance_gate_agent")
    

    # Schema extraction path
    graph.add_edge("apispec_loader_agent", "apispec_validator_agent")
    graph.add_edge("apispec_validator_agent", "schema_extraction_agent")
    graph.add_edge("schema_extraction_agent", "governance_gate_agent")
    # Backward compatibility path
    graph.add_edge("apispec_file_reader_agent", "backward_compatibility")
    graph.add_edge("backward_compatibility", "git_persistence_node")
    graph.add_edge("git_persistence_node", "governance_gate_agent")

    # API-only path
    graph.add_edge("apispec_authoring_agent", "apispec_validator_agent")
    graph.add_edge("apispec_validator_agent", "governance_gate_agent")

    # Loop back to dispatcher for next intent
    graph.add_edge("governance_gate_agent", "intent_dispatcher_agent")

    # End
    graph.add_edge("intent_dispatcher_agent", END)

    # -------------------
    # 5. Checkpointer
    # -------------------
    conn = sqlite3.connect(database="chatbot1.db", check_same_thread=False)
    checkpointer = SqliteSaver(conn=conn)

    return graph.compile(checkpointer=checkpointer)


# -------------------
# 7. Helper
# -------------------
# def retrieve_allthreads():
#     all_threads = set()
#     for checkpoint in checkpointer.list(None):
#         all_threads.add(checkpoint.config["configurable"]["thread_id"])
#     return list(all_threads)
