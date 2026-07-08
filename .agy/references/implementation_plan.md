# Implementation Plan - Python 3.13 Dependency Upgrade

This plan outlines the steps required to upgrade project dependencies and environment configurations to support **Python 3.13** as the target environment.

## User Review Required

> [!WARNING]
> Upgrading to Python 3.13 requires upgrading several key dependencies, most notably **Ray** (from `2.43.0` to `2.56.0`) and **LangChain** ecosystem packages (e.g. `langchain` from `0.3.17` to `langchain-core` versions `1.3.11` or greater). These major/minor version upgrades may introduce breaking changes or deprecations in code imports and usage across chapters.

## Open Questions

> [!IMPORTANT]
> Please review and provide feedback on the following questions:
>
> 1. **Pinning Strategy**: Should we update [requirements.txt](file:///home/user/projects/Packtpub/generative_ai_with_langchain/requirements.txt) with the exact compiled/resolved pins listed below (which ensures a stable build), or should we use relaxed version ranges (e.g. `>=`)?
> 2. **Conda Environment Configuration**: In [langchain_ai.yaml](file:///home/user/projects/Packtpub/generative_ai_with_langchain/langchain_ai.yaml), do you want to keep using the standard Conda environment structure targeting Python 3.13 (`python=3.13.12` or similar)?
> 3. **Dockerfile base image**: Do you want us to update the [Dockerfile](file:///home/user/projects/Packtpub/generative_ai_with_langchain/Dockerfile) to use a modern Python 3.13 base image (e.g., `python:3.13-slim`) instead of `continuumio/miniconda3:23.9.0-0`?

## Proposed Changes

### Configuration Updates

---

#### [MODIFY] [pyproject.toml](file:///home/user/projects/Packtpub/generative_ai_with_langchain/pyproject.toml)
- Update the Ruff target version to `py313`:
```toml
# Assume Python 3.13.
target-version = "py313"
```

#### [MODIFY] [langchain_ai.yaml](file:///home/user/projects/Packtpub/generative_ai_with_langchain/langchain_ai.yaml)
- Update Python version to `3.13` (e.g. `python=3.13.12`) or generic `python=3.13`.
- Update other package pins if required (or keep them generic/allow Conda to resolve).

#### [MODIFY] [Dockerfile](file:///home/user/projects/Packtpub/generative_ai_with_langchain/Dockerfile)
- Update the base image to support Python 3.13 (or update Conda/miniconda to install Python 3.13 environment).

### Dependency Upgrades

---

#### [MODIFY] [requirements.txt](file:///home/user/projects/Packtpub/generative_ai_with_langchain/requirements.txt)
Upgrade dependency versions to be compatible with Python 3.13:

| Package Name | Current Version | Proposed (Resolved) Version | Reason |
| :--- | :--- | :--- | :--- |
| **ray** | `2.43.0` | `2.56.0` | Ray 2.43.0 has no wheel for Python 3.13 (`cp313`). Ray 2.56.0 supports Python 3.13. |
| **langchain** | `0.3.17` | `1.3.11` | Resolves with Python 3.13 environment constraints. |
| **langchain-core** | `0.3.63` | `1.4.8` | LangChain ecosystem compatibility. |
| **langchain-community** | `0.3.16` | `0.4.2` | LangChain ecosystem compatibility. |
| **langchain-openai** | `0.3.19` | `1.3.3` | LangChain ecosystem compatibility. |
| **langchain-anthropic** | `0.3.5` | `1.4.8` | LangChain ecosystem compatibility. |
| **langchain-google-genai** | `2.0.0` | `4.2.7` | LangChain ecosystem compatibility. |
| **langchain-google-vertexai**| `>=2.0.13` | `3.2.4` | LangChain ecosystem compatibility. |
| **langchain-text-splitters** | `0.3.5` | `1.1.2` | LangChain ecosystem compatibility. |
| **langchain_huggingface** | `0.1.2` | `1.2.2` | LangChain ecosystem compatibility. |
| **langchain-ollama** | `0.2.3` | `1.1.0` | LangChain ecosystem compatibility. |
| **langchain_groq** | `0.2.4` | `1.1.3` | LangChain ecosystem compatibility. |
| **langchain-experimental** | `0.3.4` | `0.4.2` | LangChain ecosystem compatibility. |
| **langchain_chroma** | `0.2.2` | `1.1.0` | LangChain ecosystem compatibility. |
| **langchain_mistralai** | `0.2.6` | `1.1.6` | LangChain ecosystem compatibility. |
| **langsmith** | `0.3.15` | `0.9.8` | LangChain ecosystem compatibility. |
| **langgraph** | `0.3.34` | `1.2.8` | LangGraph compatibility. |
| **datasets** | `3.4.0` | `5.0.0` | Resolves with Python 3.13 constraints. |
| **arxiv** | `2.1.3` | `4.0.0` | Resolves with Python 3.13 constraints. |
| **duckduckgo_search** | `8.0.4` | `8.1.1` | Resolves with Python 3.13 constraints. |
| **huggingface-hub** | `0.28.1` | `1.22.0` | Resolves with Python 3.13 constraints. |
| **streamlit** | `1.37.1` | `1.59.0` | Resolves with Python 3.13 constraints. |
| **ruff** | `0.9.4` | `0.15.20` | Upgrade linter to match Python 3.13 support. |

## Verification Plan

### Automated Tests
- Run `uv pip compile` to verify dependency resolution works.
- Run `mypy` and linter checks (`ruff check`, or `make lint`) to catch syntax/deprecation/typing issues under the new dependency versions.

### Manual Verification
- Verify running a simple python script with the upgraded packages to check import compatibility.
