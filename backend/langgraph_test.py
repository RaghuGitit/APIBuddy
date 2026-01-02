import sys
import os

# Test imports
try:
    from langgraph_main import chatbot, retrieve_allthreads, tools
    print("✓ Successfully imported chatbot and retrieve_allthreads")
    print(f"✓ Available tools: {[tool.name for tool in tools]}")
    print("✓ langgraph_main.py compiled successfully!")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()