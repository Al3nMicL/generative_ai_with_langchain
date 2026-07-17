"""
FastAPI server for chapter 9.

Provides three endpoint flavors:
  GET  /              — browser UI
  POST /chat          — synchronous (full response at once)
  POST /chat/stream   — HTTP streaming (text/event-stream)
  WS   /ws            — WebSocket, token-by-token streaming
"""
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, model_validator

load_dotenv()

app = FastAPI(title="LangChain chat service")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant."),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

BASE_LLM_KWARGS = dict(model="gpt-3.5-turbo", temperature=0)


class ChatRequest(BaseModel):
    message: str

    @model_validator(mode="before")
    @classmethod
    def populate_message_alias(cls, values: object) -> object:
        if isinstance(values, dict) and "message" not in values and "input" in values:
            values["message"] = values["input"]
        return values


def build_chain(*, streaming: bool):
    return PROMPT | ChatOpenAI(streaming=streaming, **BASE_LLM_KWARGS) | StrOutputParser()


def build_messages(message: str) -> dict:
    return {"messages": [HumanMessage(content=message)]}


def format_sse_data(chunk: str, *, event: str | None = None) -> str:
    normalized = chunk.replace("\r\n", "\n").replace("\r", "\n")
    lines = normalized.split("\n")
    event_line = f"event: {event}\n" if event else ""
    data_lines = "".join(f"data: {line}\n" for line in lines)
    return f"{event_line}{data_lines}\n"


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    """Serve the browser chat UI."""
    return templates.TemplateResponse(request, "index.html")


@app.post("/chat")
async def chat(request: ChatRequest) -> dict:
    """Return the full LLM response in one shot."""
    response = await build_chain(streaming=False).ainvoke(build_messages(request.message))
    return {"response": response}


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest) -> StreamingResponse:
    """Stream tokens back over HTTP using SSE framing."""
    chain = build_chain(streaming=True)

    async def token_generator():
        async for chunk in chain.astream(build_messages(request.message)):
            if chunk:
                yield format_sse_data(chunk)
        yield format_sse_data("[DONE]", event="end")

    return StreamingResponse(token_generator(), media_type="text/event-stream")


@app.websocket("/ws")
async def websocket_chat(websocket: WebSocket) -> None:
    """Accept a text message per WebSocket frame; stream tokens back."""
    await websocket.accept()
    try:
        while True:
            user_input = await websocket.receive_text()
            try:
                await websocket.send_json({"sender": "bot", "message_type": "start"})
                async for token in build_chain(streaming=True).astream(
                    build_messages(user_input)
                ):
                    if token:
                        await websocket.send_json(
                            {
                                "sender": "bot",
                                "message_type": "stream",
                                "message": token,
                            }
                        )
                await websocket.send_json({"sender": "bot", "message_type": "end"})
            except Exception as exc:
                await websocket.send_json(
                    {
                        "sender": "bot",
                        "message_type": "error",
                        "message": str(exc),
                    }
                )
    except WebSocketDisconnect:
        return


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)