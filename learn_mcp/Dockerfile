FROM python:3.11-slim
WORKDIR /app
RUN pip install uv

COPY pyproject.toml uv.lock ./
RUN uv pip install --system .

COPY reseach_server.py .
EXPOSE 8080

CMD ["uv", "run", "research_server.py"]
