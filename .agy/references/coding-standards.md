# Coding Standards and Best Practices

This guide describes the coding standards, patterns, and migration guidelines required for code developed in this repository.

---

## 1. LangChain v1.x Coding Standards

This project utilizes **LangChain v1.x** running on **Python 3.13**. Follow these rules to avoid deprecation warnings and ensure code maintainability:

### Import Paths
Always use the specialized package imports instead of legacy top-level imports.

* **Incorrect (Legacy)**:
  ```python
  from langchain.chat_models import ChatOpenAI
  from langchain.document_loaders import TextLoader
  ```
* **Correct (Current)**:
  ```python
  from langchain_openai import ChatOpenAI
  from langchain_community.document_loaders import TextLoader
  ```

### LCEL (LangChain Expression Language)
Build chain components using the `Runnable` protocol instead of legacy wrappers.
* Prefer using the pipe operator (`|`) to compose prompts, models, and parsers:
  ```python
  chain = prompt | model | parser
  result = chain.invoke({"input": "value"})
  ```
* Use `ainvoke`, `astream`, and `abatch` for asynchronous applications.

---

## 2. LangGraph Design Patterns

When building stateful agents with **LangGraph v1.x** under Python 3.13:

### State Definition
Define the graph state using standard python `TypedDict` and annotate keys with appropriate reducers:
```python
from typing import Annotated, Sequence
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    # add_messages appends new messages to the existing list
    messages: Annotated[Sequence[BaseMessage], add_messages]
    sender: str
```

### Node Functions
Nodes should be pure Python functions (synchronous or asynchronous) that accept the state and return an update dictionary:
```python
async def my_node(state: AgentState) -> dict:
    messages = state["messages"]
    # Perform processing...
    return {"messages": [new_response_message], "sender": "my_node"}
```

### Compilation & Memory
Ensure the graph is compiled with a checkpointer if state memory is required across conversational turns:
```python
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)
```

---

## 3. Error Handling and Resiliency

1. **Structured Outputs**: Use `with_structured_output` on chat models to ensure the model responds according to a Pydantic schema:
   ```python
   class OutputFormat(BaseModel):
       answer: str
       sources: list[str]

   structured_llm = model.with_structured_output(OutputFormat)
   ```
2. **Fallbacks**: Always implement fallbacks for LLM calls using `.with_fallbacks()` to handle rate limits or API downtime.
3. **Traceability**: Ensure `langsmith` tracing is active during development to debug agent intermediate steps.
