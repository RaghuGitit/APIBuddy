# backend.py

import sqlite3, os, sys
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
from dotenv import load_dotenv
# from getandrun_query import getandrun
# from getandrun_erp_query import getandrun_erp
import requests
# from langchain_community.vectorstores import FAISS
# from langchain_community.embeddings import OpenAIEmbeddings
# from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()

# Add the project root (APIBUDDY) to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# -------------------
# 1. LLM
# -------------------
llm = ChatOpenAI()

# -------------------
# 2. Tools
# -------------------
# Tools
search_tool = DuckDuckGoSearchRun(region="us-en")

@tool
def calculator(first_num: float, second_num: float, operation: str) -> dict:
    """
    Perform a basic arithmetic operation on two numbers.
    Supported operations: add, sub, mul, div
    """
    try:
        if operation == "add":
            result = first_num + second_num
        elif operation == "sub":
            result = first_num - second_num
        elif operation == "mul":
            result = first_num * second_num
        elif operation == "div":
            if second_num == 0:
                return {"error": "Division by zero is not allowed"}
            result = first_num / second_num
        else:
            return {"error": f"Unsupported operation '{operation}'"}
        
        return {"first_num": first_num, "second_num": second_num, "operation": operation, "result": result}
    except Exception as e:
        return {"error": str(e)}

@tool
def create_json_schema(mandatory_fields: list, optional_fields: list) -> dict:
    """
    Create a JSON schema from lists of mandatory and optional fields.
    Args:
        mandatory_fields (list): List of field names that are required.
        optional_fields (list): List of field names that are optional.
    Returns:
        dict: JSON schema as a dictionary.
    """
    schema = {
        "type": "object",
        "properties": {},
        "required": mandatory_fields
    }
    for field in mandatory_fields:
        schema["properties"][field] = {"type": "string"}
    for field in optional_fields:
        schema["properties"][field] = {"type": "string"}
    return schema

@tool
def create_get_api_specification(api_name: str, response_json_schema: dict, method: str = "GET", endpoint: str = "/api") -> dict:
    """
    Create an HTTP-GET API specification using a JSON schema.
    Args:
        api_name (str): Name of the API.        
        response_json_schema (dict): JSON schema for the response body.
        method (str): HTTP method (default: GET).
        endpoint (str): API endpoint (default: /api).
    Returns:
        dict: API specification as a dictionary.
    """
    api_spec = {
        "openapi": "3.0.4",
        "info": {
            "title": api_name,
            "version": "0.0.1"
        },
        "servers": [
            {
                "url": "https://demo-server/v1"
            }
        ],
        "tags":[
            {
                "name": api_name
            }
        ],
        "paths": {
            f"/{endpoint}": {
                "get":{
                    "summary": f"{api_name} API",
                    "parameters":[],
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {
                                "application/json": {
                                    "schema": response_json_schema
                                }
                            }
                        },
                        "400": {
                            "description": "Bad request"
                        },
                        "500": {
                            "description": "Internal server error"
                        }
                    }

                }
                
            }
        }        
    }
    return api_spec

@tool
def create_post_api_specification(api_name: str, request_json_schema: dict, response_json_schema: dict, method: str = "POST", endpoint: str = "/api") -> dict:
    """
    Create an HTTP-POST API specification using a request and response JSON schemas.
    Args:
        api_name (str): Name of the API.        
        request_json_schema (dict): JSON schema for the request body.
        response_json_schema (dict): JSON schema for the response body.
        method (str): HTTP method (default: POST).
        endpoint (str): API endpoint (default: /api).
    Returns:
        dict: API specification as a dictionary.
    """
    api_spec = {
        "openapi": "3.0.4",
        "info": {
            "title": api_name,
            "version": "0.0.1"
        },
        "servers": [
            {
                "url": "https://demo-server/v1"
            }
        ],
        "tags":[
            {
                "name": api_name
            }
        ],
        "paths": {
            f"/{endpoint}": {
                "post":{
                    "summary": f"{api_name} API",
                    "parameters":[],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": request_json_schema
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {
                                "application/json": {
                                    "schema": response_json_schema
                                }
                            }
                        },
                        "400": {
                            "description": "Bad request",
                            "content": {
                                "application/json": {
                                    "schema": response_json_schema
                                }
                            }
                        },
                        "500": {
                            "description": "Internal server error",
                            "content": {
                                "application/json": {
                                    "schema": response_json_schema
                                }
                            }
                        }
                    }

                }
                
            }
        }        
    }
    return api_spec

@tool
def generate_api_stub_from_spec(api_spec: dict, project_name: str = "api_stub_project") -> dict:
    """
    Generate an API stub project from a given API specification and provide instructions to run it.
    Args:
        api_spec (dict): API specification dictionary.
        project_name (str): Name of the project (default: api_stub_project).
    Returns:
        dict: Project stub details including main file content and run instructions.
    """
    endpoint = api_spec.get("endpoint", "/api")
    method = api_spec.get("method", "POST").lower()
    main_file_content = f'''
from fastapi import FastAPI, Request

app = FastAPI()

@app.{method}("{endpoint}")
async def api_stub(request: Request):
    data = await request.json()
    # TODO: Implement logic based on api_spec
    return {{"message": "Stub response", "received": data}}
'''

    run_instructions = (
        "### How to run this FastAPI stub on a Windows laptop:\n"
        "1. Open Command Prompt and navigate to your project folder.\n"
        "2. (Optional) Create a virtual environment:\n"
        "   python -m venv venv\n"
        "   venv\\Scripts\\activate\n"
        "3. Install FastAPI and Uvicorn:\n"
        "   pip install fastapi uvicorn\n"
        "4. Save the stub code to a file named main.py.\n"
        "5. Start the FastAPI server:\n"
        "   uvicorn main:app --reload\n"
        "6. Open your browser and go to http://127.0.0.1:8000/docs to view the API documentation."
    )

    return {
        "project_name": project_name,
        "main_file": "main.py",
        "main_file_content": main_file_content,
        "api_spec": api_spec,
        "run_instructions": run_instructions
    }


tools = [search_tool, calculator, create_json_schema, create_get_api_specification,
         create_post_api_specification, generate_api_stub_from_spec]
llm_with_tools = llm.bind_tools(tools)

# -------------------
# 3. State
# -------------------
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# -------------------
# 4. Nodes
# -------------------
def chat_node(state: ChatState):
    """LLM node that may answer or request a tool call."""
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

tool_node = ToolNode(tools)

# -------------------
# 5. Checkpointer
# -------------------
conn = sqlite3.connect(database="chatbot1.db", check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)

# -------------------
# 6. Graph
# -------------------
graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "chat_node")

graph.add_conditional_edges("chat_node",tools_condition)
graph.add_edge('tools', 'chat_node')

chatbot = graph.compile(checkpointer=checkpointer)

# -------------------
# 7. Helper
# -------------------
def retrieve_allthreads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config["configurable"]["thread_id"])
    return list(all_threads)