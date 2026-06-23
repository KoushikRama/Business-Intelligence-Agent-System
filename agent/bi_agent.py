from llm.llm_client import call_llm


def build_bi_agent_prompt(question: str) -> str:
    return f"""
You are the routing agent for a Business Intelligence Assistant.

Choose exactly one route:

direct
sql
rag
sql_rag

Route meanings:

direct:
Use for greetings, small talk, jokes, or casual conversation.

sql:
Use when the question needs only structured database information:
customers, orders, payments, revenue, counts, totals, metrics, analytics.
choose when you are sure that document knowledge is not needed.

rag:
Use when the question needs only company document knowledge:
policies, SOPs, procedures, PTO, IT security, password policy, refund policy,
payment failure SOP, escalation guides, support procedures.
choose when you are sure that structured databse information is not needed.

sql_rag:
Use when the question needs BOTH:
1. database/business data from SQL
2. policy/SOP/procedure guidance from documents

Choose sql_rag for questions like:
- how many X and what should Y do according to policy
- count X and explain the procedure
- payment failures and what support should do
- customer/order/payment data and what the SOP says
- business metric and escalation steps

Return only one word.
Do not return JSON.
Do not explain.

Question:
{question}
"""


def rule_based_route_override(question: str, llm_choice: str) -> str:
    q = question.lower()

    sql_signals = [
        "how many",
        "count",
        "total",
        "number of",
        "revenue",
        "customers",
        "orders",
        "payments",
        "failed payments",
        "payment failures",
        "business metric",
        "analytics"
    ]

    rag_signals = [
        "policy",
        "sop",
        "procedure",
        "according to",
        "what should",
        "what does",
        "escalation",
        "guide",
        "handling",
        "support do",
        "pto",
        "leave",
        "password",
        "security",
        "refund",
        "returns"
    ]

    has_sql_signal = any(signal in q for signal in sql_signals)
    has_rag_signal = any(signal in q for signal in rag_signals)

    if has_sql_signal and has_rag_signal:
        return "sql_rag"

    return llm_choice


def decide_tool(question: str) -> str:
    prompt = build_bi_agent_prompt(question)
    response = call_llm(prompt).strip().lower()

    if "sql_rag" in response:
        llm_choice = "sql_rag"
    elif "rag" in response:
        llm_choice = "rag"
    elif "sql" in response:
        llm_choice = "sql"
    else:
        llm_choice = "direct"

    return rule_based_route_override(question, llm_choice)


def build_question_split_prompt(question: str) -> str:
    return f"""
You are helping a Business Intelligence Assistant split a mixed user question into tool-specific questions.

The original user question needs both SQL and RAG. But you must split the questions into 2 and return them in required format.

Create:
1. sql_question: only the database/metrics/count part
2. rag_question: only the policy/SOP/procedure guidance part

Rules:
- The SQL question must not mention policies, SOPs, procedures, escalation, or support guidance.
- The RAG question must not ask for database counts, totals, revenue, or metrics.
- Keep both questions short and clear.
- Return only valid JSON.
- Do not include markdown.

JSON format:
{{
  "sql_question": "...",
  "rag_question": "..."
}}

Original Question:
{question}
"""

import json
import re


def extract_json_from_llm_response(response: str) -> dict:
    cleaned = response.strip()

    cleaned = cleaned.replace("```json", "")
    cleaned = cleaned.replace("```", "")
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", cleaned, re.DOTALL)

    if match:
        return json.loads(match.group())

    raise ValueError("No valid JSON found in LLM response.")


def split_sql_rag_question(question: str) -> dict:
    prompt = build_question_split_prompt(question)
    response = call_llm(prompt)

    print(response)

    try:
        parsed = extract_json_from_llm_response(response)

        print("SQL Question:", parsed.get("sql_question"),"\nRAG Question:",parsed.get("rag_question"))

        return {
            "sql_question": parsed.get("sql_question"),
            "rag_question": parsed.get("rag_question")
        }

    except Exception:
        return {
            "sql_question": question,
            "rag_question": question
        }


def direct_response(question: str) -> str:
    prompt = f"""
You are a helpful business intelligence assistant.

The user's message does not require database or document access.
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

    if tool_choice == "sql_rag":
        split_questions = split_sql_rag_question(question)

        print("Tool choice made: sql_rag")
        print("SQL Question:", split_questions["sql_question"])
        print("RAG Question:", split_questions["rag_question"])

        return {
            "tool_choice": "sql_rag",
            "sql_question": split_questions["sql_question"],
            "rag_question": split_questions["rag_question"]
        }

    print("Tool choice made: ", tool_choice)

    return {
        "tool_choice": tool_choice
    }