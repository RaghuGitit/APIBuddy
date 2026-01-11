import os
import json
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
print("OpenAI API key loaded successfully")

def main():
    app = build_workflow()

    # Get the project root directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    api_spec_dir = os.path.join(project_root, "filesrepo", "apispecs")

    old_api_spec_dir = os.path.join(project_root, "filesrepo", "apispecs/old/old_api_spec.json")
    new_api_spec_dir = os.path.join(project_root, "filesrepo", "apispecs/new/new_api_spec.json")

    initial_state: APIBuddyState = {
        "user_goal": "Do a backward compatibility check between two API specs",
        # for comparing API specs
        "old_api_spec_path": old_api_spec_dir,
        "new_api_spec_path": new_api_spec_dir,
        "old_api_spec": None,
        "new_api_spec": None,
        "compatibility_status": None,
        "compatibility_issues": None,
        "compatibility_report": None,

        "api_spec_dir": api_spec_dir,
        "api_spec_file": "sample_api_spec.json",
        "uploaded_api_spec": None,
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

    print("\n--- FINAL STATE (JSON) ---")
    print(final_state)
    # Convert to JSON-serializable format, replacing non-serializable objects with strings
    def json_serializer(obj):
        """Handle non-serializable objects by converting them to strings."""
        try:
            return str(obj)
        except Exception:
            return repr(obj)
    
    json_output = json.dumps(final_state, indent=2, default=json_serializer)
    print(json_output)

if __name__ == "__main__":
    main()
