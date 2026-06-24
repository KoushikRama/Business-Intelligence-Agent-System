from llm.llm_client import call_llm

def build_bi_agent_prompt(question: str, recent_messages: list) -> str:
    return f"""
You are the routing agent for a Business Intelligence Assistant.

Your job is to choose EXACTLY ONE route for the current question.

Available Routes:

1. direct
2. sql
3. rag
4. sql_rag


=========================================
MEMORY USAGE RULES
=========================================

Recent messages are provided as conversation context.

Use recent messages to understand:
- follow-up questions
- references such as:
    - "them"
    - "those customers"
    - "that policy"
    - "that issue"
    - "what was my previous question"
- requests to summarize recent discussion
- requests to explain previous answers

IMPORTANT:
Choose direct if the question can be answered entirely from recent messages.

IMPORTANT:
Do NOT choose direct if fresh business data or company documents are required.

=========================================
ROUTE: direct
=========================================
choose direct when the user question doesn't involve searching database for metrics and document knowledge

Examples:
- casual talk - hi, hello, hey etc.
- non business information -sports, weather, news, casual etc.
- The question can be answered from recent messages like "what was my previous question?", "summarize what we discussed" etc.

=========================================
ROUTE: sql
=========================================

Choose sql when the question requires only structured business data.

Examples:
- customers
- orders
- payments
- revenue
- counts
- totals
- analytics
- business metrics
- customer segments
- payment statistics
- database records

Choose sql ONLY when company document knowledge is not needed.

=========================================
ROUTE: rag
=========================================

Choose rag when the question requires only company document knowledge.

Examples:
- PTO policy
- employee handbook
- SOPs
- procedures
- password policy
- IT security policy
- refund policy
- escalation guide
- support procedures

Choose rag ONLY when database information is not needed.

=========================================
ROUTE: sql_rag
=========================================

Choose sql_rag when BOTH sql aand rag are required:

1. Structured business data from SQL
2. Company policy/procedure/SOP information from documents
3. you must choose sql_rag when both 1 and 2 resources are needed to answer the question

=========================================
OUTPUT RULES
=========================================

Return ONLY one word:

direct
sql
rag
sql_rag

Do not explain.
Do not return JSON.
Do not return markdown.

Previous Recent Messages:
{recent_messages}

Current Question:
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


def decide_tool(question: str, recent_messages: str) -> str:
    prompt = build_bi_agent_prompt(question, recent_messages)
    response = call_llm(prompt).strip().lower()

    if "sql_rag" in response:
        llm_choice = "sql_rag"
    elif "rag" in response:
        llm_choice = "rag"
    elif "sql" in response:
        llm_choice = "sql"
    else:
        llm_choice = "direct"

    return llm_choice


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


def direct_response(question: str, recent_messages: list) -> str:
    prompt = f"""
You are a helpful Business Intelligence Assistant.

The current user message does NOT require database access or document retrieval.

Use the recent conversation only if it is relevant to the user's current message.

Use recent conversation for:
- answering what the previous question was
- summarizing recent discussion
- explaining a previous answer
- continuing casual context
- resolving references like "that", "it", "those", or "previous"

Do NOT invent business data.
Do NOT claim fresh database or document information.
If the question needs new database data or company policy documents, say that the request requires another tool instead of answering from memory.

Recent Conversation:
{recent_messages}

Current User Message:
{question}

Response:
"""
    return call_llm(prompt)


def bi_agent(state: dict) -> dict:
    question = state["question"]
    recent_messages = state["recent_messages"]
    tool_choice = decide_tool(question, recent_messages)

    if tool_choice == "direct":
        response = direct_response(question, recent_messages)
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