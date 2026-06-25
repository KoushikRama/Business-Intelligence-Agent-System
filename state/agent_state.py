from typing import TypedDict, Optional, List, Dict, Any


class ReactObservation(TypedDict):
    step: int
    thought: str
    action: str          # sql | rag | memory
    goal: str
    question: str
    result: Any


class AgentState(TypedDict):
    # User Input
    question: str
    conversation_id: str

    # Workflow
    workflow_choice: str
    tool_choice: Optional[str]

    # Tool Questions
    sql_question: Optional[str]
    rag_question: Optional[str]

    # Tool Results
    sql_result: Optional[Dict[str, Any]]
    rag_result: Optional[Dict[str, Any]]

    # ReAct Execution State (Ephemeral)
    react_thought: Optional[str]
    react_goal: Optional[str]
    observation_source: Optional[str]
    react_observations: List[ReactObservation]

    # Conversation Memory
    conversation_summary: str
    recent_messages: List
    historical_messages: List

    # Output
    final_response: Optional[str]
    error: Optional[str]