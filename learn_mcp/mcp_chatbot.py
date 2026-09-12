
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain_core.messages import AIMessage
import asyncio
import json

from llm_provider import get_model_id

load_dotenv()


class MCP_ChatBot:

    def __init__(self):
        self.mcp_client = None
        self.agent = None

    async def connect_to_servers(self):
        """Connect to all MCP servers defined in the configuration and build the agent."""
        try:
            with open('server_config.json', 'r') as f:
                data = json.load(f)

            servers = data.get('mcpServers', {})

            self.mcp_client = MultiServerMCPClient(servers)
            tools = await self.mcp_client.get_tools()

            print("\nConnected to MCP servers with tools:", [t.name for t in tools])

            self.agent = create_agent(get_model_id(), tools)
        except Exception as e:
            print(f"Error loading server configuration: {e}")
            raise

    async def process_query(self, query):
        result = await self.agent.ainvoke(
            {"messages": [{"role": "user", "content": query}]}
        )
        for msg in result["messages"]:
            if isinstance(msg, AIMessage):
                for call in msg.tool_calls:
                    print(f"Calling tool {call['name']} with args {call['args']}")
                if msg.content:
                    print(msg.content)

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Chatbot Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == 'quit':
                    break

                await self.process_query(query)
                print("\n")

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Cleanly close all resources."""
        pass


async def main():
    chatbot = MCP_ChatBot()
    try:
        await chatbot.connect_to_servers()
        await chatbot.chat_loop()
    finally:
        await chatbot.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
