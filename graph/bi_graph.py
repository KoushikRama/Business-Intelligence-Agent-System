from langgraph.graph import StateGraph, START, END

from state.agent_state import AgentState
from agent.bi_agent import bi_agent
from agent.response_node import response_node
from agent.memory_node import memory_node
from tools.sql_tool import sql_tool
from tools.rag_tool import rag_tool
from memory.conversation_store import save_message



def route_after_bi_agent(state: AgentState):
    tool_choice = state.get("tool_choice")

    if tool_choice == "sql":
        return "sql_tool"

    if tool_choice == "rag":
        return "rag_tool"

    if tool_choice == "sql_rag":
        return ["sql_tool", "rag_tool"]

    return END


def build_bi_graph():
    graph_builder = StateGraph(AgentState)

    graph_builder.add_node("memory_node", memory_node)
    graph_builder.add_node("bi_agent", bi_agent)
    graph_builder.add_node("sql_tool", sql_tool)
    graph_builder.add_node("rag_tool", rag_tool)
    graph_builder.add_node("response_node", response_node)

    graph_builder.add_edge(START, "memory_node")
    graph_builder.add_edge("memory_node", "bi_agent")
    graph_builder.add_conditional_edges(
        "bi_agent",
        route_after_bi_agent,
        {
            "sql_tool": "sql_tool",
            "rag_tool": "rag_tool",
            END: END
        }
    )
    graph_builder.add_edge("sql_tool", "response_node")
    graph_builder.add_edge("rag_tool", "response_node")
    graph_builder.add_edge("response_node", END)

    return graph_builder.compile()


graph = build_bi_graph()


def run_graph(question: str, conversation_id:str):
    initial_state = {
        "question": question,
        "conversation_id": conversation_id
    }

    result = graph.invoke(initial_state)

    save_message(conversation_id, "user", question)
    save_message(conversation_id, "assistant", result["final_response"])

    return result["final_response"]