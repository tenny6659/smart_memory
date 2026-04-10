import httpx
import json

url = "http://localhost:11434/api/generate"
payload = {
    "model": "llama3:latest",
    "prompt": 'Extract entities and relations from: "I work at Hexaware in Mumbai" Return JSON format: {"entities": [{"name": "...", "type": "..."}], "relations": [{"source": "User", "target": "...", "type": "..."}]}',
    "stream": False,
    "format": "json"
}

try:
    print("Calling Ollama...")
    response = httpx.post(url, json=payload, timeout=60.0)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
