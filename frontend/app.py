import sys
import os
import uuid
from dotenv import load_dotenv
# from langgraph.types import Interrupt
from langgraph.types import Command
# from langgraph.errors import GraphInterrupt

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path so imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from orchestrator.workflow import build_workflow
from state.apibuddy_state import APIBuddyState as ChatState

# To generate unique thread IDs
def generate_thread_id():
    return uuid.uuid4()

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

CONFIG = {"configurable": {"thread_id": st.session_state["thread_id"]}}

# Streamlit Page Config
st.set_page_config(
    page_title="APIBuddy",
    layout="wide"
)

st.title("APIBuddy for API Governance")

if "workflow_state" not in st.session_state:
    st.session_state.workflow_state = None

if "pending_interrupt" not in st.session_state:
    st.session_state.pending_interrupt = None

# Build LangGraph App
@st.cache_resource
def get_graph():
    return build_workflow()

app = get_graph()

# Sidebar – Show Intent and Logs
st.sidebar.header("Execution Options")

# Show the detected intent
st.sidebar.header("Detected Intent")
if st.session_state.workflow_state and st.session_state.workflow_state.get("intent"):
    st.sidebar.write(
        f"**{st.session_state.workflow_state['intent']}** "
        f"({st.session_state.workflow_state['intent_confidence']:.2f})"
    )
else:
    st.sidebar.info("Intent will be detected automatically")

# Display execution logs in sidebar
st.sidebar.header("Execution Logs")
if st.session_state.workflow_state and st.session_state.workflow_state.get("task_log"):
    with st.sidebar.expander("View Logs", expanded=True):
        for entry in st.session_state.workflow_state.get("task_log", []):
            st.write(f"- {entry}")
else:
    st.sidebar.info("No logs yet")


# requires_approval = st.sidebar.checkbox(
#     "Require Governance Approval",
#     value=True
# )

# User's input
st.subheader("User Request")

user_goal = st.text_area(
    "Describe what you want to do",
    placeholder="e.g. Compare old and new API specs for backward compatibility"
)

# -------------------------------------------------
# File Inputs (conditional)
# -------------------------------------------------
old_api_path = None
new_api_path = None
spec_dir = None
spec_file = None

# if intent == "COMPARE_API_SPECS":
#     st.subheader("API Spec Comparison Inputs")
#     old_api_path = st.text_input(
#         "Old API Spec Path",
#         "./api_specs/old/user-api.yaml"
#     )
#     new_api_path = st.text_input(
#         "New API Spec Path",
#         "./api_specs/new/user-api.yaml"
#     )

# elif intent == "EXTRACT_SCHEMAS_ONLY":
#     st.subheader("API Spec Extraction Inputs")
#     spec_dir = st.text_input(
#         "API Spec Directory",
#         "./api_specs"
#     )
#     spec_file = st.text_input(
#         "API Spec File Name",
#         "user-api.yaml"
#     )



# Interrupt Handling
if st.session_state.pending_interrupt:
    # st.info("Interrupt received - awaiting user approval")
    # st.warning("Workflow Paused - Approval Required")

    payload = st.session_state.pending_interrupt

    st.subheader("Approval Request")
    st.json(payload)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Approve"):
            # st.info("User Approved the request")
            st.session_state.workflow_state["approval_decision"] = "APPROVED"            
            st.session_state.pending_interrupt = None

            # result = app.invoke(Command(resume={"approved": 'APPROVED'}), st.session_state.workflow_state, config=CONFIG)
            result = app.invoke(
                Command(resume={"approved": 'APPROVED'}),
                config=CONFIG)
            st.session_state.workflow_state = result
            # st.success("Workflow Completed")
            interrupt_value = None

            if '__interrupt__' in result and result.get('__interrupt__') and len(result['__interrupt__']) > 0:
                interrupt_value = result['__interrupt__'][0].value
                st.session_state.workflow_state = result
                st.info("interrupt result:" + str(interrupt_value))
            # st.session_state.pending_interrupt = None                     

            if st.session_state.workflow_state:
                detected_intent = st.session_state.workflow_state.get("intent")
                confidence = st.session_state.workflow_state.get("intent_confidence")
                # if detected_intent:
                #     st.success("Intent detected by APIBuddy")
                #     # st.markdown(f"""
                #     # **Intent:** `{detected_intent}`  
                #     # **Confidence:** `{confidence:.2f}`
                #     # """)

            with st.expander("Results", expanded=True):
                if result.get("compatibility_status"):
                    st.subheader("Backward Compatibility Result")
                    st.write(result["compatibility_status"])
                    st.write(result.get("compatibility_report"))

                if result.get("json_schema"):
                    st.subheader("JSON Schema")
                    st.json(result["json_schema"])

                if result.get("api_spec"):
                    st.subheader("API Specification")
                    st.json(result["api_spec"])
             
            # Check if interrupt is present in result
            if interrupt_value is not None:            
                st.info("Interrupt received - awaiting user approval")
                st.session_state.pending_interrupt = interrupt_value
                st.rerun()        

    with col2:
        if st.button("Reject"):
            st.info("User Rejected the request")
            st.session_state.workflow_state["approval_decision"] = "REJECTED"            
            st.session_state.pending_interrupt = None
            result = app.invoke(
                Command(resume={"approved": 'REJECTED'}),
                config=CONFIG)
            st.session_state.workflow_state = result
            # st.success("Workflow Completed")

            try:
                result = app.invoke(
                Command(resume={"approved": 'REJECTED'}),
                config=CONFIG)
                st.session_state.workflow_state = result
                # st.success("Workflow Completed")
                with st.expander("Results", expanded=True):
                    if result.get("compatibility_status"):
                        st.subheader("Backward Compatibility Result")
                        st.write(result["compatibility_status"])
                        st.write(result.get("compatibility_report"))

                    if result.get("json_schema"):
                        st.subheader("JSON Schema")
                        st.json(result["json_schema"])

                    if result.get("api_spec"):
                        st.subheader("API Specification")
                        st.json(result["api_spec"])
            except Exception as e:
                st.error("User rejected the request - Workflow terminated")
                st.write(str(e))

# Run Button
if st.button("▶ Run APIBuddy"):    
    
    if not user_goal:
        st.error("Please provide a user request")
        st.stop()

    # -------------------------------
    # Initialize State
    # -------------------------------
    initial_state: ChatState = {
        "user_goal": user_goal,
        "intent": None,
        "intent_confidence": None,

        # File-based inputs
        "old_api_spec_path": old_api_path,
        "new_api_spec_path": new_api_path,
        "api_spec_dir": spec_dir,
        "api_spec_file": spec_file,

        # Runtime fields
        "json_schema": None,
        "api_spec": None,

        # Validation
        "schema_is_valid": None,
        "api_spec_is_valid": None,

        # Governance
        "requires_approval": True,
        "pending_approval": None,
        "approval_decision": None,

        # Audit
        "task_log": []
    }

    st.info("Executing workflow...")

    try:
        
        result = app.invoke(initial_state, config=CONFIG)
        interrupt_value = None

        if '__interrupt__' in result and result.get('__interrupt__') and len(result['__interrupt__']) > 0:
            interrupt_value = result['__interrupt__'][0].value
            st.session_state.workflow_state = result
            st.info("interrupt result:" + str(interrupt_value))
            st.session_state.pending_interrupt = None
        
        # Check if interrupt is present in result
        if interrupt_value is not None:            
            st.info("Interrupt received - awaiting user approval")
            st.session_state.pending_interrupt = interrupt_value
            st.rerun()
        
        if st.session_state.workflow_state:
            detected_intent = st.session_state.workflow_state.get("intent")
            confidence = st.session_state.workflow_state.get("intent_confidence")
            # if detected_intent:
            #     st.success("Intent detected by APIBuddy")
            #     # st.markdown(f"""
            #     # **Intent:** `{detected_intent}`  
            #     # **Confidence:** `{confidence:.2f}`
            #     # """)

        # Show Results
        if st.session_state.workflow_state and not st.session_state.pending_interrupt:
            result = st.session_state.workflow_state
            # st.info("Trace1")

            # st.success("Workflow Completed")

            with st.expander("Results", expanded=True):
                if result.get("compatibility_status"):
                    st.subheader("Backward Compatibility Result")
                    st.write(result["compatibility_status"])
                    st.write(result.get("compatibility_report"))

                if result.get("json_schema"):
                    st.subheader("JSON Schema")
                    st.json(result["json_schema"])

                if result.get("api_spec"):
                    st.subheader("API Specification")
                    st.json(result["api_spec"])


    # except GraphInterrupt as interrupt:
    #     # Workflow paused
    #     print("Workflow paused for approval")
    #     print("Interrupt payload:", interrupt.value)
    #     st.info("Interrupt received - awaiting user approval")
    #     st.session_state.workflow_state = interrupt.state
    #     st.session_state.pending_interrupt = interrupt.value
    #     st.rerun()

    except Exception as e:
        st.info("Exception")
        st.error("Execution failed")
        st.exception(e)

