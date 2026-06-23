from llm.llm_client import call_llm


def build_bi_agent_prompt(question: str) -> str:
    return f"""
You are a Business Intelligence Agent.

Your job is to decide whether the user's question needs the SQL tool.

Use SQL tool for:
- customers
- orders
- payments
- revenue
- business performance
- metrics
- counts
- analytics
- employees
- salaries
- restricted access questions
- insert/update/delete requests
- external questions that cannot be answered from company schema

Do NOT use SQL tool for:
- greetings
- small talk
- jokes
- casual conversation

Return ONLY one word:
SQL
or
DIRECT

User Question:
{question}
"""


def decide_tool(question: str) -> str:
    prompt = build_bi_agent_prompt(question)
    response = call_llm(prompt).strip().upper()

    if "SQL" in response:
        return "sql"

    return "direct"


def direct_response(question: str) -> str:
    prompt = f"""
You are a helpful business intelligence assistant.

The user's message does not require database access.
Respond naturally and concisely.

User Message:
{question}
"""
    return call_llm(prompt)


def bi_agent(state: dict) -> dict:
    question = state["question"]
    tool_choice = decide_tool(question)

    if tool_choice == "direct":
        response = direct_response(question)
        return {
            "tool_choice": "direct",
            "final_response": response
        }

    return {
        "tool_choice": "sql"
    }