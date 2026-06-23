from llm.llm_client import call_llm


def build_response_prompt(question: str, sql_result: dict) -> str:
    return f"""
You are a business intelligence assistant.

Your job is to answer the user's question using only the SQL result provided.

Rules:
- Be concise and business-friendly.
- Do not invent data.
- If the SQL result contains a message, explain that message directly.
- If the SQL result has an error, explain that the query could not be completed.
- If the SQL result is empty, say no matching records were found.

User Question:
{question}

SQL Query Used:
{sql_result.get("sql_query")}

SQL Results:
{sql_result.get("results")}

SQL Error:
{sql_result.get("error")}

Final Answer:
"""


def response_node(state: dict) -> dict:
    question = state["question"]
    sql_result = state.get("sql_result")

    if not sql_result:
        return {
            "final_response": "No SQL result was available to answer the question."
        }

    prompt = build_response_prompt(question, sql_result)
    response = call_llm(prompt)

    return {
        "final_response": response
    }