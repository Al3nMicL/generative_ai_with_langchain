---
name: agy
description: Guidelines and planning procedures for developing, debugging, and modifying LangChain and LangGraph agent code in this workspace.
---

# Agent Documentation and Planning

Welcome to the `generative_ai_with_langchain` workspace developer agent guidelines. This directory is structured following the [Agent Skills Folder Specification](https://agentskills.io/specification) to provide guidelines, planning templates, reference architectures, and scripting utilities for developing LLM and agentic workflows using LangChain and LangGraph.

## Directory Structure

This skill directory contains the following components:
- `SKILL.md`: Main instructions and directory overview (this file).
- [references/architecture.md](references/architecture.md): Reference multi-agent and RAG architectures used in the project.
- [references/coding-standards.md](references/coding-standards.md): Guidelines on Python 3.13, LangChain v1.x, LangGraph nodes/edges structure, and typing.
- [assets/plan-template.md](assets/plan_template.md): Template to structure agent implementation plans before modifying code.
- [assets/langgraph-template.py](assets/langgraph_template.py): Starter code template for building new LangGraph workflows.
- [scripts/validate-workspace.py](scripts/validate_workspace.py): Python utility script to verify environment compatibility and imports.

---

## Workspace Navigation & Guidelines

This workspace is a structured code companion to the book **Generative AI with LangChain, Second Edition**. It is split into chapter-based folders (`chapter1` to `chapter9`) and standalone project packages (e.g., `writing_assistant`).

When implementing new features, debugging existing ones, or writing tests:
1. **Always plan first**: Create a planning document based on [assets/plan-template.md](assets/plan_template.md) to define scope, changes, and testing strategies.
2. **Consult references**: Follow the [references/coding-standards.md](references/coding-standards.md) to ensure correct LangChain and LangGraph patterns.
3. **Execute validation**: Use [scripts/validate-workspace.py](scripts/validate_workspace.py) to check imports and Python version requirements.

## How to Proceed with Coding Tasks

1. **Understand Chapter Scopes**: Keep chapter-specific examples intact unless explicitly requested to update/debug them. For new projects, use the root or create a custom chapter directory.
2. **Environment & Dependency Management**: Refer to [SETUP.md](file:///home/user/projects/Packtpub/generative_ai_with_langchain/SETUP.md) and [pyproject.toml](file:///home/user/projects/Packtpub/generative_ai_with_langchain/pyproject.toml). Make sure you run commands inside the correct virtual environment.
