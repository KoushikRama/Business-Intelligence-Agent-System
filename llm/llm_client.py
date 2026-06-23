import os
import requests
from dotenv import load_dotenv

load_dotenv()


def call_llm(prompt: str) -> str:
    ollama_url = os.environ.get("OLLAMA_URL")
    model_name = os.environ.get("OLLAMA_MODEL")

    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(ollama_url, json=payload)
    response.raise_for_status()

    return response.json()["response"]