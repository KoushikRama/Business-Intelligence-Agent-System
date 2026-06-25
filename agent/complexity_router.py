from llm.llm_client import call_llm


def build_complexity_router_prompt(
    question: str,
    conversation_summary: str | None,
    recent_messages: list,
    historical_messages: list
) -> str:
    return f"""
You are a workflow complexity router for a Business Intelligence Assistant.

Choose exactly one workflow:

simple_workflow
react_workflow

=========================================
WORKFLOW: simple_workflow
=========================================

Use for normal questions that can be answered in one pass.

Examples:
- greetings
- memory recall
- previous question
- summarize recent conversation
- simple SQL questions
- simple RAG questions
- simple SQL + RAG questions
- normal follow-up questions where the reference is clear

=========================================
WORKFLOW: react_workflow
=========================================

Use when the question may need limited iterative reasoning.

Choose basic_react for:
- ambiguous follow-up questions
- questions likely needing clarification
- user says "try again"
- user says "fix that"
- user corrects previous interpretation
- previous tool result failed
- SQL query may need one retry
- the assistant may need to inspect one result before deciding next step
- analyze why
- investigate
- root cause
- compare multiple factors
- find trends
- diagnose business issue
- generate recommendations
- multi-step BI analysis
- Choose react_workflow for questions asking to explain mismatch, inconsistency, or confusion about previous tool results.

=========================================
IMPORTANT RULES
=========================================

Prefer simple_workflow unless the question clearly needs ReAct.

Do not choose react_workflow for simple count, policy, or memory questions.

Return only one word:
simple_workflow
react_workflow


Conversation Summary:
{conversation_summary}

Recent Messages:
{recent_messages}

Historical Messages:
{historical_messages}

Current Question:
{question}
"""


def route_workflow(
    question: str,
    conversation_summary: str | None = None,
    recent_messages: list | None = None,
    historical_messages: list | None = None
) -> str:
    recent_messages = recent_messages or []
    historical_messages = historical_messages or []

    prompt = build_complexity_router_prompt(
        question=question,
        conversation_summary=conversation_summary,
        recent_messages=recent_messages,
        historical_messages=historical_messages
    )

    response = call_llm(prompt).strip().lower()

    if "react_workflow" in response:
        return "react_workflow"

    return "simple_workflow"

def rule_based_workflow_route(question: str) -> str:
    q = question.lower()

    react_signals = [
        "analyze",
        "investigate",
        "root cause",
        "why",
        "recommend",
        "recommend actions",
        "doesn't look right",
        "not right",
        "wrong",
        "try again",
        "check again",
        "recheck",
        "inconsistent",
        "mismatch",
        "verify",
        "compare",
        "diagnose"
    ]

    if any(signal in q for signal in react_signals):
        return "react_workflow"

    return "simple_workflow"

def complexity_router_node(state: dict) -> dict:
    question = state["question"]

    workflow_choice = route_workflow(
        question=question,
        conversation_summary=state.get("conversation_summary"),
        recent_messages=state.get("recent_messages", []),
        historical_messages=state.get("historical_messages", [])
    )

    # workflow_choice = rule_based_workflow_route(question)

    print("Workflow choice made:", workflow_choice)

    return {
        "workflow_choice": workflow_choice
    }