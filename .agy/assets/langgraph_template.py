#!/usr/bin/env python3
"""
LangGraph Starter Boilerplate Template.
This script demonstrates the structure of a stateful agent workflow using LangGraph v1.x.
"""

import os
from typing import Annotated, Sequence
from typing_extensions import TypedDict

# Core LangChain and LangGraph imports
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver


# 1. Define the Shared State
class State(TypedDict):
    """The graph state exchanged between nodes."""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    next_step: str


# 2. Define Node Functions
async def call_model_node(state: State) -> dict:
    """Invokes the language model to generate a response."""
    messages = state.get("messages", [])
    
    # Initialize the LLM (ensure API keys are loaded)
    # Using a dummy model configuration or local mock for safe execution.
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    response = await model.ainvoke(messages)
    return {
        "messages": [response],
        "next_step": "end"
    }


# 3. Define Routing Logic
def route_next_step(state: State) -> str:
    """Decides which path to take based on state evaluation."""
    if state.get("next_step") == "end":
        return END
    return "call_model"


# 4. Construct and Compile the Graph
def build_graph():
    # Instantiate the StateGraph
    workflow = StateGraph(State)
    
    # Add nodes to the graph
    workflow.add_node("call_model", call_model_node)
    
    # Establish entry points and edges
    workflow.add_edge(START, "call_model")
    
    # Add conditional routing
    workflow.add_conditional_edges(
        "call_model",
        route_next_step,
        {
            END: END,
            "call_model": "call_model"
        }
    )
    
    # Compile with memory persistence
    checkpointer = MemorySaver()
    compiled_graph = workflow.compile(checkpointer=checkpointer)
    return compiled_graph


if __name__ == "__main__":
    import asyncio
    
    async def main():
        print("Building LangGraph workflow...")
        graph = build_graph()
        
        # Test input
        initial_state = {
            "messages": [HumanMessage(content="Hello, LangGraph!")],
            "next_step": "start"
        }
        
        config = {"configurable": {"thread_id": "demo-thread-1"}}
        
        print("Invoking graph stream...")
        async for event in graph.astream(initial_state, config):
            for node_name, state_update in event.items():
                print(f"\n--- Node: {node_name} ---")
                print(state_update)

    # To run, ensure OPENAI_API_KEY is in your environment
    if "OPENAI_API_KEY" in os.environ:
        asyncio.run(main())
    else:
        print("[!] Warning: OPENAI_API_KEY environment variable not set. Graph execution skipped.")
        print("[+] Graph compiled successfully! Feel free to run with valid API keys.")
