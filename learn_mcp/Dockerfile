# Use the official lightweight Python 3.12 slim image as the base
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Install 'uv', a fast Python package and project manager
RUN pip install uv

# Copy project dependency and lock files first to leverage Docker layer caching
COPY pyproject.toml uv.lock ./

# Install the project and its dependencies into the system Python environment
RUN uv pip install --system .

# Copy the server application code into the container
COPY research_server.py .

# Expose port 8080 for incoming network traffic/MCP server communication
EXPOSE 8080

# Specify the command to run when the container starts
ENTRYPOINT ["uv", "run", "research_server.py"]
