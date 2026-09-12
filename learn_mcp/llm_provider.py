import os


def get_model_id() -> str:
    """Build the 'provider:model' identifier LangChain's create_agent/
    init_chat_model expects, from env vars set in .env."""
    provider = os.environ["LLM_PROVIDER"]
    model = os.environ["LLM_MODEL"]
    return f"{provider}:{model}"
