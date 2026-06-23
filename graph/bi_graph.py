from langgraph.graph import StateGraph, START, END

from state.agent_state import AgentState
from agent.bi_agent import bi_agent
from agent.response_node import response_node
from tools.sql_tool import sql_tool


def route_after_bi_agent(state: AgentState):
    tool_choice = state.get("tool_choice")

    if tool_choice == "sql":
        return "sql_tool"

    return END


def build_bi_graph():
    graph_builder = StateGraph(AgentState)

    graph_builder.add_node("bi_agent", bi_agent)
    graph_builder.add_node("sql_tool", sql_tool)
    graph_builder.add_node("response_node", response_node)

    graph_builder.add_edge(START, "bi_agent")

    graph_builder.add_conditional_edges(
        "bi_agent",
        route_after_bi_agent,
        {
            "sql_tool": "sql_tool",
            END: END
        }
    )

    graph_builder.add_edge("sql_tool", "response_node")
    graph_builder.add_edge("response_node", END)

    return graph_builder.compile()

graph = build_bi_graph()

def run_graph(question: str):

    initial_state = {
        "question": question,
        "tool_choice": None,
        "sql_result": None,
        "final_response": None,
        "error": None
    }

    result = graph.invoke(initial_state)

    return result["final_response"]