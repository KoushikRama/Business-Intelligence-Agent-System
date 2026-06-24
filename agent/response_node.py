from llm.llm_client import call_llm


def format_rag_context(rag_result: dict | None) -> str:
    if not rag_result:
        return ""

    retrieved_chunks = rag_result.get("retrieved_chunks", [])

    if not retrieved_chunks:
        return ""

    context = ""

    for index, chunk in enumerate(retrieved_chunks, start=1):
        source_file = chunk.get("source_file", "Unknown source")
        content = chunk.get("content", "")

        context += f"""
Source {index}: {source_file}
Content:
{content}
"""

    return context

def build_response_prompt(
    question: str,
    sql_result: dict | None = None,
    rag_result: dict | None = None,
    recent_messages: list | None = None
) -> str:

    rag_context = format_rag_context(rag_result)

    return f"""
You are a Business Intelligence Assistant.

Your job is to answer the user's question using the available information.

Available Information:
1. Recent Conversation
2. SQL Results
3. Company Document Context

=========================================
USAGE RULES
=========================================

Use Recent Conversation for:
- answering questions about previous messages
- summarizing recent discussion
- explaining previous answers
- resolving references such as:
  - it
  - that
  - those
  - previous question
  - previous answer

Use SQL Results for:
- counts
- totals
- revenue
- orders
- customers
- payments
- business metrics

Use Company Document Context for:
- policies
- SOPs
- procedures
- employee guidelines
- escalation guides

If both SQL and document context are available:
- combine them into a single answer.

If Recent Conversation alone answers the question:
- answer directly from memory.
- do not mention SQL or documents.

If information is missing:
- say so clearly.
- do not invent facts.

Be concise and business-friendly.

=========================================
USER QUESTION
=========================================

{question}

=========================================
RECENT CONVERSATION
=========================================

{recent_messages}

=========================================
SQL RESULT
=========================================

{sql_result}

=========================================
DOCUMENT CONTEXT
=========================================

{rag_context}

=========================================
FINAL ANSWER
=========================================
"""


def response_node(state: dict) -> dict:
    question = state["question"]

    sql_result = state.get("sql_result")
    rag_result = state.get("rag_result")
    recent_messages = state.get("recent_messages")

    if not sql_result and not rag_result:
        return {
            "final_response": "No information was available to answer the question."
        }

    prompt = build_response_prompt(
        question=question,
        sql_result=sql_result,
        rag_result=rag_result,
        recent_messages=recent_messages
    )

    response = call_llm(prompt)

    return {
        "final_response": response
    }