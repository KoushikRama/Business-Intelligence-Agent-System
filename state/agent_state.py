from typing import TypedDict, Optional, List, Dict, Any


class AgentState(TypedDict):
    question: str
    tool_choice: Optional[str]
    sql_question: str
    rag_question:str
    sql_result: Optional[Dict[str, Any]]
    rag_result: dict
    conversation_id: str
    conversation_summary: str
    recent_messages: list
    historical_messages: list
    final_response: Optional[str]
    error: Optional[str]