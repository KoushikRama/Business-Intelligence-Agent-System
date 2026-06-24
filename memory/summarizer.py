from llm.llm_client import call_llm
from memory.conversation_store import get_all_messages
from database.queries import execute_insert_query, execute_select_query


def get_conversation_summary(conversation_id: str) -> str | None:
    query = f"""
    SELECT summary_text
    FROM conversation_summaries
    WHERE conversation_id = '{conversation_id}';
    """

    rows = execute_select_query(query)

    if not rows:
        return None

    return rows[0]["summary_text"]


def save_conversation_summary(conversation_id: str, summary_text: str) -> None:
    safe_summary = summary_text.replace("'", "''")

    query = f"""
    INSERT INTO conversation_summaries(
        conversation_id,
        summary_text,
        updated_at
    )
    VALUES (
        '{conversation_id}',
        '{safe_summary}',
        CURRENT_TIMESTAMP
    )
    ON CONFLICT (conversation_id)
    DO UPDATE SET
        summary_text = EXCLUDED.summary_text,
        updated_at = CURRENT_TIMESTAMP;
    """

    execute_insert_query(query)


def build_summary_prompt(messages: list[dict]) -> str:
    return f"""
You are summarizing a conversation for a Business Intelligence Assistant.

Create a compact memory summary for future LLM prompts.

Goal:
Preserve only information useful for future conversation.

Include:
- User goals
- Important findings
- Key business metrics
- Important policy conclusions
- Clarifications and references
- Unresolved issues

Do NOT:
- Use tables
- Use markdown
- Repeat information
- Write explanations

IMPORTANT: Keep summary under 100 words.

Do not include unnecessary small talk.
Do not invent facts.
Keep the summary in concise bullets.

Conversation Messages:
{messages}

Summary:
"""


def summarize_conversation(conversation_id: str) -> str:
    messages = get_all_messages(conversation_id)

    if not messages:
        return ""

    prompt = build_summary_prompt(messages)
    summary = call_llm(prompt)

    save_conversation_summary(conversation_id, summary)

    return summary