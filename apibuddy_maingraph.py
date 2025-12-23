from langgraph.graph import StateGraph, START, END
from typing import List, TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model='gpt-5')

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    user_input: str
    user_intent: str
    spec_content: str
    common_components: dict
    version_info: dict
    compatibility_report: dict
    generated_artifacts: dict
    human_approval: bool
    notification_targets: List[str]

def chat_node(state: ChatState):
    messages = state['messages']
    response = llm.invoke(messages)
    return {"messages": [response]}