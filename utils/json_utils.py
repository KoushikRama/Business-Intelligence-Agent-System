import json
import re

def extract_json_from_llm_response(response: str) -> dict:
    cleaned = response.strip()

    cleaned = cleaned.replace("```json", "")
    cleaned = cleaned.replace("```", "")
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", cleaned, re.DOTALL)

    if match:
        return json.loads(match.group())

    raise ValueError("No valid JSON found in LLM response.")
