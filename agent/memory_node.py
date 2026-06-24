from memory.conversation_store import get_recent_messages, create_conversation

def memory_node(state: dict) -> dict:
    conversation_id = state.get("conversation_id")

    if not conversation_id:
        return {
            "recent_messages":[]
        }
    
    recent_messages = get_recent_messages(
        conversation_id=conversation_id,
        limit=12
    )

    return{
        "recent_messages":recent_messages
    }