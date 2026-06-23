from database.schema_reader import get_database_schema
from database.queries import execute_select_query
from llm.llm_client import call_llm


def build_sql_prompt(user_question: str) -> str:
    schema_text = get_database_schema()
    return f"""
You are a PostgreSQL SQL generation tool for a Business Intelligence platform.

Your job is to generate ONE valid PostgreSQL SELECT query.

Database Access Policy:
- The database is READ ONLY.
- Never generate INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, CREATE, GRANT, or REVOKE.
- If the user asks to modify, delete, insert, update, create, drop, or change records, return:
SELECT 'This request is not allowed because the system only supports read-only database access.' AS message;

Allowed Business Data:
- Users may access customer analytics.
- Users may access order analytics.
- Users may access payment analytics.
- Users may access payment failure counts, payment statuses, payment methods, failure reasons, and payment amounts.
- Users may access business metrics such as counts, totals, averages, revenue, order status, and customer segments.

Restricted Data:
- Users may NOT access employee salaries.
- Users may NOT access private employee HR records.
- Users may NOT access passwords, secrets, tokens, or authentication credentials.
- If the user asks for restricted employee/private/security data, return:
SELECT 'You do not have permission to access this information.' AS message;

Schema Rules:
- Use ONLY tables and columns present in the schema.
- Never invent table names.
- Never invent column names.
- Never invent filters, values, joins, regions, states, statuses, dates, or business rules that are not requested by the user.
- If the question cannot be answered from the schema, return:
SELECT 'Question cannot be answered from available schema.' AS message;

External Topic Rules:
- If the question is about external topics such as weather, sports, stock prices, news, celebrities, or public events, return:
SELECT 'Question cannot be answered from available schema.' AS message;

SQL Rules:
- Return ONLY SQL.
- No markdown.
- No explanations.
- Query must start with SELECT.
- Use PostgreSQL syntax.
- Prefer simple queries over complex queries.
- Do not generate subqueries unless absolutely necessary.
- Do not generate CTEs.
- Do not generate window functions.
- Use ILIKE for text filters.
- When using JOINs, always use table aliases.
- When using JOINs, always qualify column names with aliases.
- Never use unqualified column names in JOIN queries.

Aggregation Rules:
- If COUNT(), SUM(), AVG(), MIN(), MAX() are used:
  - Every non-aggregated selected column must appear in GROUP BY.
- Never mix aggregate and non-aggregate columns without GROUP BY.

Database Schema:
{schema_text}

User Question:
{user_question}
"""

def clean_sql(sql_text: str) -> str:
    return (
        sql_text
        .replace("```sql", "")
        .replace("```", "")
        .strip()
    )


def generate_sql(user_question: str) -> str:
    prompt = build_sql_prompt(user_question)
    llm_response = call_llm(prompt)
    return clean_sql(llm_response)


def validate_sql(sql_query: str) -> bool:
    normalized = sql_query.strip().upper()

    if not normalized.startswith("SELECT"):
        return False

    blocked_keywords = [
        "INSERT", "UPDATE", "DELETE", "DROP", "ALTER",
        "TRUNCATE", "CREATE", "GRANT", "REVOKE"
    ]

    for keyword in blocked_keywords:
        if keyword in normalized:
            return False

    return True


def sql_tool(state: dict) -> dict:
    question = state.get("sql_question", state["question"])
    sql_query = generate_sql(question)
    print("SQL Tool Generated SQL:", sql_query)

    if not validate_sql(sql_query):
        return {
            "sql_result": {
                "success": False,
                "tool": "sql",
                "sql_query": sql_query,
                "results": [],
                "error": "Generated SQL violated read-only policy."
            },
            "error": "SQL validation failed."
        }

    try:
        results = execute_select_query(sql_query)

        return {
            "sql_result": {
                "success": True,
                "tool": "sql",
                "sql_query": sql_query,
                "results": results,
                "error": None
            }
        }

    except Exception as error:
        return {
            "sql_result": {
                "success": False,
                "tool": "sql",
                "sql_query": sql_query,
                "results": [],
                "error": str(error)
            },
            "error": str(error)
        }