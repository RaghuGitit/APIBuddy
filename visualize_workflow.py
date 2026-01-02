import os
from dotenv import load_dotenv
load_dotenv()

from orchestrator.workflow import build_workflow

def visualize_workflow():
    app = build_workflow()
    
    # Generate PNG image
    image_data = app.get_graph().draw_mermaid_png()
    
    # Save to file
    output_path = "workflow_diagram.png"
    with open(output_path, "wb") as f:
        f.write(image_data)
    
    print(f"✓ Workflow diagram saved to {output_path}")
    
    # Also print ASCII representation
    print("\n--- Workflow Structure ---")
    print(app.get_graph().draw_ascii())

if __name__ == "__main__":
    visualize_workflow()