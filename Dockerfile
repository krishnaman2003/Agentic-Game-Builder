FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create output directory
RUN mkdir -p /app/output

# The container connects to an Ollama server running on the host.
# Pass OLLAMA_BASE_URL to point at your Ollama instance.
# Example: docker run -e OLLAMA_BASE_URL=http://host.docker.internal:11434/v1 ...

ENTRYPOINT ["python", "main.py"]
