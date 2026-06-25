from llm.llm_client import call_llm
from utils.json_utils import extract_json_from_llm_response

from tools.sql_tool import sql_tool
from tools.rag_tool import rag_tool

from agent.question_transformers.sql_transformer import rewrite_sql_question
from agent.question_transformers.rag_transformer import rewrite_rag_question
from agent.react_prompts import build_final_answer_prompt,build_memory_observation_prompt,build_react_decision_prompt

MAX_REACT_STEPS = 4




def decide_next_react_step(state: dict, observations: list) -> dict:
    prompt = build_react_decision_prompt(state, observations)
    response = call_llm(prompt)

    try:
        parsed = extract_json_from_llm_response(response)

        return {
            "thought": parsed.get("thought", ""),
            "action": parsed.get("action", "clarify"),
            "goal": parsed.get("goal", ""),
            "clarification_question": parsed.get("clarification_question")
        }

    except Exception:
        return {
            "thought": "Could not parse ReAct decision.",
            "action": "clarify",
            "goal": "Ask the user for clarification.",
            "clarification_question": "Can you clarify what you mean?"
        }




def run_memory_observation(
    state: dict,
    observations: list,
    react_thought: str,
    react_goal: str
) -> str:
    prompt = build_memory_observation_prompt(
        state=state,
        observations=observations,
        react_thought=react_thought,
        react_goal=react_goal
    )

    return call_llm(prompt)




def final_answer_from_observations(
    state: dict,
    observations: list,
    react_thought: str,
    react_goal: str
) -> dict:
    prompt = build_final_answer_prompt(
        state=state,
        observations=observations,
        react_thought=react_thought,
        react_goal=react_goal
    )

    response = call_llm(prompt)

    return {
        "final_response": response
    }


def run_sql_observation(
    state: dict,
    step: int,
    react_thought: str,
    react_goal: str
) -> dict:
    sql_question = rewrite_sql_question(
        question=state["question"],
        react_thought=react_thought,
        react_goal=react_goal,
        conversation_summary=state.get("conversation_summary"),
        recent_messages=state.get("recent_messages", []),
        historical_messages=state.get("historical_messages", [])
    )

    print("ReAct SQL Question:", sql_question)

    tool_state = {
        **state,
        "tool_choice": "sql",
        "sql_question": sql_question,
        "rag_question": None,
        "react_thought": react_thought,
        "react_goal": react_goal,
        "observation_source": "sql"
    }

    sql_output = sql_tool(tool_state)

    return {
        "step": step,
        "thought": react_thought,
        "action": "sql",
        "goal": react_goal,
        "question": sql_question,
        "result": sql_output.get("sql_result")
    }


def run_rag_observation(
    state: dict,
    step: int,
    react_thought: str,
    react_goal: str
) -> dict:
    rag_question = rewrite_rag_question(
        question=state["question"],
        react_thought=react_thought,
        react_goal=react_goal,
        conversation_summary=state.get("conversation_summary"),
        recent_messages=state.get("recent_messages", []),
        historical_messages=state.get("historical_messages", [])
    )

    print("ReAct RAG Question:", rag_question)

    tool_state = {
        **state,
        "tool_choice": "rag",
        "sql_question": None,
        "rag_question": rag_question,
        "react_thought": react_thought,
        "react_goal": react_goal,
        "observation_source": "rag"
    }

    rag_output = rag_tool(tool_state)

    return {
        "step": step,
        "thought": react_thought,
        "action": "rag",
        "goal": react_goal,
        "question": rag_question,
        "result": rag_output.get("rag_result")
    }


def run_memory_observation_step(
    state: dict,
    observations: list,
    step: int,
    react_thought: str,
    react_goal: str
) -> dict:
    memory_result = run_memory_observation(
        state=state,
        observations=observations,
        react_thought=react_thought,
        react_goal=react_goal
    )

    return {
        "step": step,
        "thought": react_thought,
        "action": "memory",
        "goal": react_goal,
        "question": state.get("question"),
        "result": memory_result
    }


def react_agent(state: dict) -> dict:
    observations = state.get("react_observations", [])

    latest_thought = state.get("react_thought") or ""
    latest_goal = state.get("react_goal") or ""
    latest_action = state.get("observation_source") or None

    for step_index in range(len(observations), MAX_REACT_STEPS):
        step_number = step_index + 1

        decision = decide_next_react_step(
            state=state,
            observations=observations
        )

        latest_thought = decision.get("thought", "")
        latest_goal = decision.get("goal", "")
        action = decision.get("action", "clarify")
        latest_action = action

        print(f"ReAct Step {step_number}")
        print("Thought:", latest_thought)
        print("Action:", action)
        print("Goal:", latest_goal)

        if action == "clarify":
            return {
                **state,
                "react_thought": latest_thought,
                "react_goal": latest_goal,
                "observation_source": "clarify",
                "react_observations": observations,
                "final_response": decision.get("clarification_question")
                or "Can you clarify what you mean?"
            }

        if action == "memory":
            observation = run_memory_observation_step(
                state=state,
                observations=observations,
                step=step_number,
                react_thought=latest_thought,
                react_goal=latest_goal
            )

            observations.append(observation)
            continue

        if action == "sql":
            observation = run_sql_observation(
                state=state,
                step=step_number,
                react_thought=latest_thought,
                react_goal=latest_goal
            )

            observations.append(observation)
            continue

        if action == "rag":
            observation = run_rag_observation(
                state=state,
                step=step_number,
                react_thought=latest_thought,
                react_goal=latest_goal
            )

            observations.append(observation)
            continue

        if action == "final":
            final_response = final_answer_from_observations(
                state=state,
                observations=observations,
                react_thought=latest_thought,
                react_goal=latest_goal
            )

            return {
                **state,
                "react_thought": latest_thought,
                "react_goal": latest_goal,
                "observation_source": "final",
                "react_observations": observations,
                **final_response
            }

    final_response = final_answer_from_observations(
        state=state,
        observations=observations,
        react_thought=latest_thought,
        react_goal=latest_goal
    )

    return {
        **state,
        "react_thought": latest_thought,
        "react_goal": latest_goal,
        "observation_source": latest_action or "max_steps_reached",
        "react_observations": observations,
        **final_response
    }