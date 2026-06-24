from llm.llm_client import call_llm
from agent.question_transformers.rag_transformer import rewrite_rag_question
from agent.question_transformers.sql_transformer import rewrite_sql_question
from agent.question_transformers.sql_rag_transformer import split_sql_rag_question
from agent.response_node import direct_response
from agent.agent_prompts import build_bi_agent_prompt, build_direct_response_prompt

def decide_tool(question: str, recent_messages: str, historical_messages: list, conversation_summary:str) -> str:
    prompt = build_bi_agent_prompt(question, recent_messages, historical_messages, conversation_summary)
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

def bi_agent(state: dict) -> dict:
    question = state["question"]
    recent_messages = state["recent_messages"]
    historical_messages = state["historical_messages"]
    conversation_summary = state["conversation_summary"]
    tool_choice = decide_tool(question, recent_messages, historical_messages, conversation_summary)

    if tool_choice == "direct":
        prompt = build_direct_response_prompt(question, recent_messages, historical_messages, conversation_summary)
        response = direct_response(prompt)
        return {
            "tool_choice": "direct",
            "final_response": response
        }
    
    if tool_choice == "sql":
        sql_question = rewrite_sql_question(
            question,
            recent_messages,
            historical_messages,
            conversation_summary
        )
        print("SQL Question:", sql_question)

        return {
            "tool_choice": "sql",
            "sql_question": sql_question,
            "rag_question": None
        }
    
    if tool_choice == "rag":
        rag_question = rewrite_rag_question(
            question,
            recent_messages,
            historical_messages,
            conversation_summary
        )
        print("RAG Question:", rag_question)

        return {
            "tool_choice": "rag",
            "sql_question": None,
            "rag_question": rag_question
        }

    if tool_choice == "sql_rag":
        split_questions = split_sql_rag_question(question, recent_messages, historical_messages, conversation_summary)
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