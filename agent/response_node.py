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
    rag_result: dict | None = None
) -> str:

    rag_context = format_rag_context(rag_result)

    return f"""
You are a Business Intelligence Assistant.

Your job is to answer the user's question using the available tool results.

Rules:
- Use only the provided SQL result and/or retrieved document context.
- Do not invent facts.
- If SQL result is available, use it for business numbers and metrics.
- If document context is available, use it for policies, SOPs, procedures, and guidance.
- If both SQL and document context are available, combine them naturally.
- If the answer is not available in the provided information, say so clearly.
- Be concise and business-friendly.
- Mention source document names when answering from documents.

User Question:
{question}

SQL Result:
{sql_result}

Retrieved Document Context:
{rag_context}

Final Answer:
"""


def response_node(state: dict) -> dict:
    question = state["question"]

    sql_result = state.get("sql_result")
    rag_result = state.get("rag_result")

    if not sql_result and not rag_result:
        return {
            "final_response": "No information was available to answer the question."
        }

    prompt = build_response_prompt(
        question=question,
        sql_result=sql_result,
        rag_result=rag_result
    )

    response = call_llm(prompt)

    return {
        "final_response": response
    }