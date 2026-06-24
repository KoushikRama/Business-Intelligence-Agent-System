from llm.llm_client import call_llm
from utils.json_utils import extract_json_from_llm_response

def build_rag_rewrite_prompt(
    question: str,
    recent_messages: list,
    historical_messages: list
) -> str:
    return f"""
You rewrite a user's follow-up question into a clear RAG-focused question.

The rewritten question will be sent to a document retrieval tool.

Use memory only to resolve references like:
- that policy
- that SOP
- that procedure
- it
- previous document
- above

Rules:
- Return only valid JSON.
- Do not include markdown.
- Do not ask for database counts, totals, metrics, revenue, customers, orders, or payments.
- Do not invent facts.
- Keep the rewritten question short and specific.
- If the question is already clear, return it unchanged.

JSON format:
{{
  "rag_question": "..."
}}

Current Question:
{question}

Recent Messages:
{recent_messages}

Historical Messages:
{historical_messages}
"""

def rewrite_rag_question(
    question: str,
    recent_messages: list,
    historical_messages: list
) -> str:
    prompt = build_rag_rewrite_prompt(
        question,
        recent_messages,
        historical_messages
    )

    response = call_llm(prompt)

    try:
        parsed = extract_json_from_llm_response(response)
        return parsed.get("rag_question")
    except Exception:
        return question