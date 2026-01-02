import os
from dotenv import load_dotenv
load_dotenv()

from orchestrator.workflow import build_workflow
from state.apibuddy_state import APIBuddyState

# ---- LangSmith (optional but recommended) ----
# os.environ["LANGCHAIN_TRACING_V2"] = "true"
# os.environ["LANGCHAIN_PROJECT"] = "apibuddy"
# os.environ["LANGCHAIN_API_KEY"] = "<LANGSMITH_KEY>"
# os.environ["OPENAI_API_KEY"] = "<OPENAI_KEY>"

# Verify API key is loaded
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in .env file")
print("✓ OpenAI API key loaded successfully")

def main():
    app = build_workflow()

    initial_state: APIBuddyState = {
        "user_goal": "I Dont know",
        "json_schema": None,
        "schema_name": None,
        "api_spec": None,
        "linked_components": None,
        "schema_explanation": None,
        "requires_approval": True,
        "approval_status": None,
        "task_log": []
    }

    final_state = app.invoke(initial_state)

    print("\n--- FINAL STATE ---")
    print(final_state)

if __name__ == "__main__":
    main()
