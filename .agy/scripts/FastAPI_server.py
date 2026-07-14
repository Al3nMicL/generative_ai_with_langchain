"""
FastAPI server for chapter 9 — lanarky replacement.

Implements the same three endpoint flavors that lanarky's LangchainRouter
used to generate automatically:
  POST /chat          — synchronous (full response at once)
  POST /chat/stream   — HTTP streaming (text/event-stream)
  WS   /ws            — WebSocket, token-by-token streaming

Requires:
    pip install fastapi uvicorn python-dotenv langchain-openai langchain-core
"""
import asyncio

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

load_dotenv()

# ---------------------------------------------------------------------------
# App & shared prompt template
# ---------------------------------------------------------------------------
app = FastAPI(title="LangChain chat service")

# A minimal conversational prompt.
# Swap system text or add MessagesPlaceholder("history") if you add memory.
PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant."),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

BASE_LLM_KWARGS = dict(model="gpt-3.5-turbo", temperature=0)


# ---------------------------------------------------------------------------
# Request schema
# ---------------------------------------------------------------------------
class ChatRequest(BaseModel):
    input: str


# ---------------------------------------------------------------------------
# 1.  POST /chat  — synchronous, full response
# ---------------------------------------------------------------------------
@app.post("/chat")
async def chat(request: ChatRequest) -> dict:
    """Return the full LLM response in one shot."""
    chain = PROMPT | ChatOpenAI(**BASE_LLM_KWARGS) | StrOutputParser()
    response = await chain.ainvoke(
        {"messages": [HumanMessage(content=request.input)]}
    )
    return {"response": response}


# ---------------------------------------------------------------------------
# 2.  POST /chat/stream  — HTTP streaming (text/event-stream)
# ---------------------------------------------------------------------------
@app.post("/chat/stream")
async def chat_stream(request: ChatRequest) -> StreamingResponse:
    """Stream tokens back over HTTP as plain text chunks."""
    chain = PROMPT | ChatOpenAI(streaming=True, **BASE_LLM_KWARGS) | StrOutputParser()

    async def token_generator():
        async for chunk in chain.astream(
            {"messages": [HumanMessage(content=request.input)]}
        ):
            if chunk:
                yield chunk

    return StreamingResponse(token_generator(), media_type="text/event-stream")


# ---------------------------------------------------------------------------
# 3.  WS /ws  — WebSocket, token-by-token streaming
#
# Concurrency note: we need to *run* the chain and *consume* its output at
# the same time.  asyncio.create_task() lets the LLM invocation run in the
# background while the outer loop forwards tokens to the client as they
# arrive.  Getting this wrong (e.g. awaiting the task first) will cause the
# WebSocket to block until the full answer is ready.
# ---------------------------------------------------------------------------
@app.websocket("/ws")
async def websocket_chat(websocket: WebSocket) -> None:
    """Accept a text message per WebSocket frame; stream tokens back."""
    await websocket.accept()
    try:
        while True:
            user_input = await websocket.receive_text()

            # Build a fresh chain per message so callbacks never bleed
            # between requests (the old shared-ConversationChain anti-pattern).
            chain = (
                PROMPT
                | ChatOpenAI(streaming=True, **BASE_LLM_KWARGS)
                | StrOutputParser()
            )

            # Fire the chain as a background task so we can iterate tokens
            # while it is still running.
            invoke_task = asyncio.create_task(
                chain.ainvoke({"messages": [HumanMessage(content=user_input)]})
            )

            # astream() yields string chunks directly through StrOutputParser.
            async for token in chain.astream(
                {"messages": [HumanMessage(content=user_input)]}
            ):
                if token:
                    await websocket.send_text(token)

            # Signal end-of-turn to the client.
            await websocket.send_text("[DONE]")

            # Ensure the background task is cleaned up even if astream
            # finished first.
            try:
                await invoke_task
            except Exception:
                pass

    except WebSocketDisconnect:
        pass


# ---------------------------------------------------------------------------
# Dev entrypoint
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
