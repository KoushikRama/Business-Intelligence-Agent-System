from llm.llm_client import call_llm
from agent.agent_prompts import build_response_node_prompt

def direct_response(prompt: str) -> str:
    return call_llm(prompt)

def response_node(state: dict) -> dict:
    question = state["question"]

    sql_result = state.get("sql_result")
    rag_result = state.get("rag_result")
    recent_messages = state.get("recent_messages")
    historical_messages = state.get("historical_messages")
    conversation_summary = state.get("conversation_summary")
    react_thought = state.get("react_thought")
    react_goal = state.get("react_goal")

    if not sql_result and not rag_result:
        return {
            "final_response": "No information was available to answer the question."
        }

    prompt = build_response_node_prompt(
        question=question,
        sql_result=sql_result,
        rag_result=rag_result,
        recent_messages=recent_messages,
        historical_messages = historical_messages,
        conversation_summary=conversation_summary,
        react_thought=react_thought,
        react_goal=react_goal
    )

    response = call_llm(prompt)


    return {
        "final_response": response
    }