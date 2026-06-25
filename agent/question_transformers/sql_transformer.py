from llm.llm_client import call_llm
from utils.json_utils import extract_json_from_llm_response


def build_sql_rewrite_prompt(
    question: str,
    recent_messages: list,
    historical_messages: list,
    conversation_summary: str | None = None,
    react_thought: str | None = None,
    react_goal: str | None = None
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

Use the ReAct Thought and ReAct Goal to understand what the SQL query should verify, inspect, compare, or retrieve.
Do not treat the ReAct Thought or ReAct Goal as facts.
They are only the agent's current reasoning objective.

Rules:
- Return only valid JSON.
- Do not include markdown.
- Do not ask for policies, SOPs, procedures, or document guidance.
- Do not invent facts.
- Do not create raw SQL.
- Return a natural-language SQL question.
- Do not invent table names or column names.
- The SQL question must only ask for database information.
- Never include SOP, policy, document, support actions, procedures, or guidance.
- If the ReAct Goal contains both SQL and policy needs, extract only the SQL/database part.
- Ask for the needed business information and let the SQL generator use the schema.
- Keep the rewritten question short, simple and specific.
- If the question is already clear, return it unchanged.

JSON format:
{{
  "sql_question": "..."
}}

Current Question:
{question}

ReAct Thought:
{react_thought}

ReAct Goal:
{react_goal}

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
    conversation_summary: str | None = None,
    react_thought: str | None = None,
    react_goal: str | None = None
) -> str:
    prompt = build_sql_rewrite_prompt(
        question=question,
        recent_messages=recent_messages,
        historical_messages=historical_messages,
        conversation_summary=conversation_summary,
        react_thought=react_thought,
        react_goal=react_goal
    )

    response = call_llm(prompt)

    try:
        parsed = extract_json_from_llm_response(response)
        return parsed.get("sql_question") or question
    except Exception:
        return question