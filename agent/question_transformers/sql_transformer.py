from llm.llm_client import call_llm
from utils.json_utils import extract_json_from_llm_response

def build_sql_rewrite_prompt(
    question: str,
    recent_messages: list,
    historical_messages: list,
    conversation_summary: str
) -> str:
    return f"""
You rewrite a user's follow-up question into a clear SQL-focused question.

The rewritten question will be sent to a SQL generation tool.

Use memory only to resolve references like:
- they
- their
- those customers
- that group
- previous result
- above

Rules:
- Return only valid JSON.
- Do not include markdown.
- Do not ask for policies, SOPs, procedures, or document guidance.
- Do not invent facts.
- Keep the rewritten question short and specific.
- If the question is already clear, return it unchanged.

JSON format:
{{
  "sql_question": "..."
}}

Current Question:
{question}

Conversation Summary:
{conversation_summary}

Recent Messages:
{recent_messages}

Historical Messages:
{historical_messages}
"""

def rewrite_sql_question(
    question: str,
    recent_messages: list,
    historical_messages: list,
    conversation_summary: str
) -> str:
    prompt = build_sql_rewrite_prompt(
        question,
        recent_messages,
        historical_messages,
        conversation_summary
    )

    response = call_llm(prompt)

    try:
        parsed = extract_json_from_llm_response(response)
        return parsed.get("sql_question")
    except Exception:
        return question
