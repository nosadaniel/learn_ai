# 🧠 Learn AI: Hands-on AI, LLMs & Model Context Protocol (MCP) Projects

A comprehensive collection of practical projects exploring **Artificial Intelligence (AI)**, **Large Language Models (LLMs)**, **Agentic Architectures**, and the **Model Context Protocol (MCP)**.

---

## 📚 Repository Overview

| Module / Project | Description | Key Technologies |
| :--- | :--- | :--- |
| **[`learn_mcp/`](./learn_mcp)** | Research assistant chatbot combining **FastMCP** server with **Claude 3.7 Sonnet** to search and analyze arXiv scientific papers in real-time. | Model Context Protocol (MCP), Claude 3.7 Sonnet, FastMCP, arXiv API, `uv` |

---

## 🎯 Focus Areas

1. **AI & Large Language Models (LLMs)**
   - Agentic loops and multi-step reasoning
   - Tool calling and structured schema generation
   - Prompt engineering and context management
2. **Model Context Protocol (MCP)**
   - Building custom FastMCP servers over `stdio`
   - Connecting LLM clients to MCP servers via `ClientSession`
   - Visual debugging and schema validation with `@modelcontextprotocol/inspector`
3. **Applied AI Tooling & Integrations**
   - Live external API integrations (e.g. arXiv, scientific literature)
   - Dynamic caching and structured data storage

---

## 🚀 Getting Started

To explore the projects, navigate to any specific project directory and follow its dedicated `README.md`.

### Example: Running the MCP Project
```bash
# Navigate to learn_mcp
cd learn_mcp

# Install dependencies with uv
uv sync

# Configure your API key
cp .env.example .env

# Run the MCP research chatbot
uv run mcp_chatbot.py
```

---

## 📄 License

MIT License
