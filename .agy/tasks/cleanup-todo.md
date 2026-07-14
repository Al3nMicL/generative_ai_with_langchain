# cleanup-todo.md
<!-- Tasks for CLI agents. Each task is self-contained with all context needed to execute it. -->

---

## Task 1 — Ruff lint auto-fix

**Priority:** Low  
**Effort:** Minutes  
**Branch:** `verify` (or a new `chore/ruff-fix` branch off `verify`)

### What to do

Run the ruff auto-fixer against the project, review the diff, then commit:

```bash
# From project root, using the workspace venv:
.venv/bin/ruff check . --fix
.venv/bin/ruff check . --statistics   # should show only non-fixable issues remaining
git diff
git add -A
git commit -m "chore: auto-fix ruff lint issues (unsorted imports, unused imports, f-strings)"
```

### Expected outcome after `--fix`

| Rule | Count before | Should be 0 after fix |
|------|-------------|----------------------|
| `I001` unsorted-imports | 178 | ✅ auto-fixable |
| `F401` unused-import | 28 | ✅ auto-fixable |
| `F541` f-string-no-placeholders | 2 | ✅ auto-fixable |

### Remaining non-fixable (do NOT touch — leave for a separate PR)

| Rule | Count | Reason |
|------|-------|--------|
| `E501` line-too-long | 119 | Style decision; needs manual wrap or config change |
| `E402` module-import-not-at-top-of-file | 25 | Intentional patterns (e.g. `set_environment()` before imports) |
| `F811` redefined-while-unused | 8 | Possible logic issues — needs human review |
| `F821` undefined-name | 5 | Likely missing imports or stubs — needs human review |
| `F841` local-variable-assigned-but-never-used | 2 | Needs human review |

**Do not attempt to fix `E402`, `F811`, `F821`, or `F841` automatically.** Only apply `--fix`, nothing more.

---

## Task 2 — Rewrite `chapter9/chat.py` (remove `lanarky`)

**Priority:** Medium  
**Effort:** ~30–60 min  
**Branch:** new branch `chore/remove-lanarky` off `verify`

### Context

`chapter9/chat.py` was originally adapted from the unmaintained `lanarky` library
(`https://github.com/ajndkr/lanarky`). `lanarky` is not in `requirements.txt`, is
incompatible with LangChain ≥1.x, and will cause an `ImportError` at runtime.

The project already has a working reference implementation of the same pattern at
[`chapter9/fastapi/main.py`](../chapter9/fastapi/main.py) — a pure FastAPI +
LangChain streaming server using `AsyncIteratorCallbackHandler` and WebSockets.
**Use that file as the implementation template.**

### Current behaviour of `chapter9/chat.py`

```python
# Broken — lanarky not installed, incompatible with LangChain 1.x
from lanarky import LangchainRouter          # ← ImportError
from langchain.chains import ConversationChain

langchain_router = LangchainRouter(...)
langchain_router.add_langchain_api_route(...)
langchain_router.add_langchain_api_websocket_route(...)
app.include_router(langchain_router)
```

The file exposed three routes:
- `GET /` — serves `chapter9/templates/index.html` via Jinja2
- `POST /chat` — single-turn JSON response (non-streaming)
- `GET /chat_json` — JSON response (streaming_mode=2, lanarky-specific)
- `WS /ws` — WebSocket streaming

### What to build

Rewrite **`chapter9/chat.py` in-place** (do not create a new file). Preserve the
same route surface:

| Route | Method | Behaviour |
|-------|--------|-----------|
| `/` | `GET` | Serve `chapter9/templates/index.html` via `Jinja2Templates` |
| `/chat` | `POST` | Accept `{"message": "..."}` JSON body; return `{"response": "..."}` (non-streaming, `ChatOpenAI` invoke) |
| `/chat_json` | `POST` | Same as `/chat` — this was lanarky's streaming_mode=2 which returned full JSON; keep as a plain invoke alias so existing callers don't break |
| `/ws` | `WebSocket` | Stream tokens using `AsyncIteratorCallbackHandler` + `ChatOpenAI(streaming=True)` |

### Constraints

- **Keep `ChatOpenAI`** as the LLM (the original used `ChatOpenAI`; do NOT switch to Anthropic).
- **Keep `config.set_environment()`** call at module startup.
- **Templates directory** is `chapter9/templates/` (contains `index.html`). The Jinja2 path must be relative-safe — use `Path(__file__).parent / "templates"`.
- **No new dependencies** — only use packages already in `requirements.txt`:
  `fastapi`, `langchain-openai`, `langchain-core`, `starlette`, `uvicorn`.
- `langchain.callbacks.AsyncIteratorCallbackHandler` → import from
  `langchain_core.callbacks` if the `langchain.callbacks` path is removed in 1.x
  (check at implementation time; fall back to `langchain.callbacks` if still present).
- Add `if __name__ == "__main__": uvicorn.run(...)` block on port `8000`.
- Update the module docstring to remove the lanarky reference.

### Verification steps (run after rewriting)

```bash
# 1. Confirm no ImportError:
.venv/bin/python -c "import chapter9.chat"

# 2. Start the server and hit the health route:
cd chapter9
.venv/bin/uvicorn chat:app --port 8001 &
curl -s http://localhost:8001/ | head -5
kill %1

# 3. Ruff clean on the rewritten file:
.venv/bin/ruff check chapter9/chat.py
```

### Commit message

```
fix(chapter9): replace lanarky with native FastAPI + LangChain streaming

lanarky is unmaintained and incompatible with LangChain >=1.x.
Reimplemented chat.py using AsyncIteratorCallbackHandler + WebSockets,
matching the pattern already used in chapter9/fastapi/main.py.

Routes preserved: GET /, POST /chat, POST /chat_json, WS /ws.
```
