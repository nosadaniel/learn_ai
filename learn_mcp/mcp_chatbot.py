
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain_core.messages import AIMessage
from mcp.types import PromptArgument
from pydantic import BaseModel
import asyncio
import json

from llm_provider import get_model_id

load_dotenv()


class AvailablePrompt(BaseModel):
    name: str
    server_name: str
    description: str | None = None
    arguments: list[PromptArgument] = []


class AvailableResource(BaseModel):
    uri: str
    server_name: str
    name: str | None = None
    description: str | None = None
    mime_type: str | None = None


class MCP_ChatBot:

    def __init__(self):
        self.mcp_client = None
        self.agent = None
        self.server_names = []
        self.available_prompts: dict[str, AvailablePrompt] = {}
        self.available_resources: dict[str, AvailableResource] = {}

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

            self.server_names = list(servers.keys())
            await self._discover_prompts_and_resources()
        except Exception as e:
            print(f"Error loading server configuration: {e}")
            raise

    async def _discover_prompts_and_resources(self):
        """List prompts/resources on each server so they can be resolved by name later."""
        for server_name in self.server_names:
            try:
                async with self.mcp_client.session(server_name) as session:
                    try:
                        prompts_response = await session.list_prompts()
                        for prompt in prompts_response.prompts:
                            self.available_prompts[prompt.name] = AvailablePrompt(
                                name=prompt.name,
                                server_name=server_name,
                                description=prompt.description,
                                arguments=prompt.arguments or [],
                            )
                    except Exception:
                        pass

                    try:
                        resources_response = await session.list_resources()
                        for resource in resources_response.resources:
                            uri = str(resource.uri)
                            self.available_resources[uri] = AvailableResource(
                                uri=uri,
                                server_name=server_name,
                                name=resource.name,
                                description=resource.description,
                                mime_type=resource.mimeType,
                            )
                    except Exception:
                        pass
            except Exception:
                continue

    async def _run_agent(self, messages):
        result = await self.agent.ainvoke({"messages": messages})
        for msg in result["messages"]:
            if isinstance(msg, AIMessage):
                for call in msg.tool_calls:
                    print(f"Calling tool {call['name']} with args {call['args']}")
                if msg.content:
                    print(msg.content)

    async def process_query(self, query):
        await self._run_agent([{"role": "user", "content": query}])

    async def list_prompts(self):
        """Print all prompts discovered across connected MCP servers."""
        if not self.available_prompts:
            print("No prompts available.")
            return
        print("\nAvailable prompts:")
        for prompt in self.available_prompts.values():
            print(f"- {prompt.name}: {prompt.description or ''}")
            for arg in prompt.arguments:
                required = " (required)" if arg.required else ""
                print(f"    - {arg.name}{required}: {arg.description or ''}")

    async def execute_prompt(self, prompt_name, args):
        """Render an MCP prompt and run the result through the agent."""
        prompt = self.available_prompts.get(prompt_name)
        if not prompt:
            print(f"Prompt '{prompt_name}' not found.")
            return
        try:
            messages = await self.mcp_client.get_prompt(prompt.server_name, prompt_name, arguments=args)
        except Exception as e:
            print(f"Error executing prompt '{prompt_name}': {e}")
            return
        print(f"\nExecuting prompt '{prompt_name}'...")
        await self._run_agent(messages)

    async def get_resource(self, resource_uri):
        """Read and print an MCP resource's content."""
        resource = self.available_resources.get(resource_uri)
        server_names = [resource.server_name] if resource else self.server_names
        for name in server_names:
            try:
                blobs = await self.mcp_client.get_resources(server_name=name, uris=resource_uri)
            except Exception:
                continue
            if blobs:
                print(f"\nResource: {resource_uri}")
                for blob in blobs:
                    print(blob.as_string())
                return
        print(f"Resource '{resource_uri}' not found.")

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Chatbot Started!")
        print("Type your queries or 'quit' to exit.")
        print("Use @folders to see available topics")
        print("Use @<topic> to search papers in that topic")
        print("Use /prompts to list available prompts")
        print("Use /prompt <name> <arg1=value1> to execute a prompt")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if not query:
                    continue

                if query.lower() == 'quit':
                    break

                if query.startswith('@'):
                    topic = query[1:]
                    resource_uri = "papers://folders" if topic == "folders" else f"papers://{topic}"
                    await self.get_resource(resource_uri)
                elif query.startswith('/'):
                    parts = query.split()
                    command = parts[0].lower()
                    if command == '/prompts':
                        await self.list_prompts()
                    elif command == '/prompt':
                        if len(parts) < 2:
                            print("Usage: /prompt <name> [key=value ...]")
                        else:
                            prompt_name = parts[1]
                            args = dict(
                                arg.split('=', 1) for arg in parts[2:] if '=' in arg
                            )
                            await self.execute_prompt(prompt_name, args)
                    else:
                        print(f"Unknown command: {command}")
                else:
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
