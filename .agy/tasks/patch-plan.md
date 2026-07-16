# PR #1 review + parallel execution plan

## Review findings against required fixes

1. **API compatibility broken** in `chapter9/fastapi/main.py`:
    - Request model only accepts `input`, but prior usage expects `message`.
    - No alias/backward-compat handling.
2. **SSE framing is incorrect**:
    - `POST /chat/stream` returns raw chunks with `text/event-stream` but does not emit SSE frames (`data: ...\n\n`).
3. **WebSocket streaming invokes chain twice**:
    - Current code runs both `chain.ainvoke(...)` and `chain.astream(...)`.
    - This duplicates LLM work and can produce inconsistent behavior.
4. **Root route removed**:
    - README says to open `http://localhost:8000`, but `GET /` is absent in `chapter9/fastapi/main.py`.
5. **Environment loading mismatch**:
    - Code imports/uses `python-dotenv` (`load_dotenv`) but `requirements.txt` does not include `python-dotenv`.
6. **Cleanup doc outdated**:
    - `.agy/tasks/cleanup-todo.md` still references `AsyncIteratorCallbackHandler` migration framing; needs LCEL `chain.astream()` update.
7. **Regression tests missing**:
    - No tests currently cover request compatibility, SSE framing, WS streaming semantics, or env-loading behavior.

## Parallel multi-chat execution plan

### Tab A — API + streaming behavior (core code changes)
- File: `chapter9/fastapi/main.py`
- Changes:
    - Add request model compatibility: `message` primary field + `input` alias support.
    - Fix SSE framing in `/chat/stream` (`data: <chunk>\n\n`, terminal event optional but consistent).
    - Refactor `/ws` to use only `chain.astream()` (remove background `ainvoke` path).
    - Restore `GET /` route aligned with README and existing template.

### Tab B — environment + docs updates
- Files: `requirements.txt`, `chapter9/fastapi/main.py`, `.agy/tasks/cleanup-todo.md`, `chapter9/README.md` (if needed)
- Changes:
    - Choose one path and apply consistently:
        - **Preferred:** remove `load_dotenv()` and use existing `config.set_environment()` pattern, or
        - add `python-dotenv` explicitly to `requirements.txt`.
    - Update cleanup task doc to describe LCEL streaming (`chain.astream`) and remove lanarky-era guidance.
    - Ensure README route text matches actual root endpoint behavior.

### Tab C — regression tests
- New tests under `chapter9/fastapi/tests/` (or project test convention if required):
    - API compatibility test: accepts both `{"message": "..."} and {"input": "..."}`.
    - SSE correctness test: verifies `text/event-stream` payload is framed as SSE.
    - WebSocket streaming test: validates streamed tokens and end-of-turn marker without double invocation semantics.
    - Environment loading test: verifies chosen env strategy is wired (no missing dependency path).
- Tests should mock LLM chain/astream to avoid network/API-key dependence.

## Integrated validation tasks (after merge of tabs)

1. `ruff check chapter9/fastapi/main.py chapter9/fastapi/tests`
2. `python -m unittest discover -s chapter9/fastapi/tests -p "test_*.py"`
3. Smoke run:
    - `cd chapter9/fastapi`
    - `python main.py`
    - confirm `GET /` serves UI and `/chat`, `/chat/stream`, `/ws` contracts hold.

## Merge order

1. Tab A (core behavior)
2. Tab B (env/docs consistency)
3. Tab C rebased on A+B (tests reflecting final contracts)
