from database.schema_reader import get_database_schema
from database.queries import execute_select_query
from llm.llm_client import call_llm


def build_sql_prompt(user_question: str) -> str:
    schema_text = get_database_schema()
    return f"""
You are a PostgreSQL SQL generation agent for a Business Intelligence platform.

Your job is to generate ONE valid PostgreSQL SELECT query.

Database Access Policy:
- The database is READ ONLY.
- Never generate INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, CREATE, GRANT, or REVOKE.
- If the user asks to modify data, return:

SELECT 'This request is not allowed because the system only supports read-only database access.' AS message;

User Access Policy:
- Users may access customer, order, and payment analytics.
- Users may NOT access employee salaries or private employee information.
- If restricted information is requested, return:

SELECT 'You do not have permission to access this information.' AS message;

Schema Rules:
- Use ONLY tables and columns present in the schema.
- Never invent table names.
- Never invent column names.
- If the question cannot be answered from the schema, return:
SELECT 'Question cannot be answered from available schema.' AS message;

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
- Do not guess values that do not exist in the schema.
- When using JOINs, always use table aliases.
- When using JOINs, always qualify column names with aliases.
- Never use unqualified column names in JOIN queries.

Aggregation Rules:
- If COUNT(), SUM(), AVG(), MIN(), MAX() are used:
  - Every non-aggregated selected column must appear in GROUP BY.
- Never mix aggregate and non-aggregate columns without GROUP BY.

Examples:

Question:
How is the business doing?

SQL:
SELECT 
    COUNT(DISTINCT c.customer_id) AS total_customers,
    COUNT(o.order_id) AS total_orders,
    SUM(o.total_amount) AS total_revenue
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id;

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
    question = state["question"]
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