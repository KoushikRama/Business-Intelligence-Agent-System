from llm.llm_client import call_llm
from utils.json_utils import extract_json_from_llm_response


def build_sql_rag_split_prompt(
    question: str,
    recent_messages: list,
    historical_messages: list,
    conversation_summary: str | None = None,
    react_thought: str | None = None,
    react_goal: str | None = None
) -> str:
    return f"""
You are helping a Business Intelligence Assistant split a mixed user question into tool-specific questions.

The original user question needs both SQL and RAG.

Use memory only to resolve references like:
- they
- their
- those customers
- that policy
- that SOP
- previous result
- previous document

Use the ReAct Thought and ReAct Goal to understand what each tool-specific question should accomplish.
Do not treat the ReAct Thought or ReAct Goal as facts.
They are only the agent's current reasoning objective.

Create:
1. sql_question: only the database/metrics/count part
2. rag_question: only the policy/SOP/procedure/document guidance part

Rules:
- Return only valid JSON.
- Do not include markdown.
- Do not invent facts.
- The SQL question must not mention policies, SOPs, procedures, escalation, or support guidance.
- The RAG question must not ask for database counts, totals, revenue, or metrics.
- Keep both questions short and clear.

JSON format:
{{
  "sql_question": "...",
  "rag_question": "..."
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


def split_sql_rag_question(
    question: str,
    recent_messages: list,
    historical_messages: list,
    conversation_summary: str | None = None,
    react_thought: str | None = None,
    react_goal: str | None = None
) -> dict:
    prompt = build_sql_rag_split_prompt(
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

        return {
            "sql_question": parsed.get("sql_question") or question,
            "rag_question": parsed.get("rag_question") or question
        }

    except Exception:
        return {
            "sql_question": question,
            "rag_question": question
        }