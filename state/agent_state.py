from typing import TypedDict, Optional, List, Dict, Any


class AgentState(TypedDict):
    question: str
    tool_choice: Optional[str]
    sql_result: Optional[Dict[str, Any]]
    final_response: Optional[str]
    error: Optional[str]