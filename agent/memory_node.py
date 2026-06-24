from memory.conversation_store import get_recent_messages
from memory.memory_vector_store import retrieve_historical_messages

def memory_node(state: dict) -> dict:
    conversation_id = state.get("conversation_id")
    question = state.get("question")

    if not conversation_id:
        return {
            "recent_messages":[],
            "historical_messages":[]
        }
    
    recent_messages = get_recent_messages(
        conversation_id=conversation_id,
        limit=6
    )

    historical_messages = retrieve_historical_messages(
        conversation_id=conversation_id,
        query=question,
        top_k=3
    )

    return{
        "recent_messages":recent_messages,
        "historical_messages": historical_messages
    }