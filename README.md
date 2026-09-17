# 🧠 Learn AI: Hands-on AI, LLMs & Model Context Protocol (MCP) Projects

A comprehensive collection of practical projects exploring **Artificial Intelligence (AI)**, **Large Language Models (LLMs)**, **Agentic Architectures**, and the **Model Context Protocol (MCP)**.

---

## 📚 Repository Overview

| Module / Project | Description | Key Technologies |
| :--- | :--- | :--- |
| **[`learn_mcp/`](./learn_mcp)** | Research assistant chatbot combining **FastMCP** server with LangChain to search and analyze arXiv scientific papers in real-time. | Model Context Protocol (MCP), LangChain, FastMCP, arXiv API, `uv` |

---
## CI/CD flow
```mermaid
flowchart TD
    A["Push / PR / Tag / Manual Dispatch"] --> B["main.yml (Orchestrator)"]
    B --> C["Job: detect-changes (dorny/paths-filter@v3)"]
    C -->|"learn_mcp changed OR Tag pushed"| D["Call: build-push-research-mcp.yml"]
    C -->|"Future: learn_rag changed"| E["Call: build-push-rag.yml"]
```

## 📄 License

MIT License
