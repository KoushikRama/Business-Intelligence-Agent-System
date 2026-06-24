import uuid

from database.queries import execute_insert_query, execute_select_query


def create_conversation() -> str:
    conversation_id = str(uuid.uuid4())

    query = f"""
    INSERT INTO conversations(conversation_id)
    VALUES ('{conversation_id}');
    """

    execute_insert_query(query)

    return conversation_id


def save_message(conversation_id: str, role: str, message: str) -> None:
    message_id = str(uuid.uuid4())

    safe_message = message.replace("'", "''")

    query = f"""
    INSERT INTO messages(
        message_id,
        conversation_id,
        role,
        message_text
    )
    VALUES (
        '{message_id}',
        '{conversation_id}',
        '{role}',
        '{safe_message}'
    );
    """

    execute_insert_query(query)


def get_recent_messages(conversation_id: str, limit: int) -> list[dict]:
    query = f"""
    SELECT role, message_text
    FROM (
        SELECT role, message_text, created_at
        FROM messages
        WHERE conversation_id = '{conversation_id}'
        ORDER BY created_at DESC
        LIMIT {limit}
    ) recent_messages
    ORDER BY created_at ASC;
    """

    return execute_select_query(query)


def get_all_messages(conversation_id: str) -> list[dict]:
    query = f"""
    SELECT role, message_text
    FROM messages
    WHERE conversation_id = '{conversation_id}'
    ORDER BY created_at ASC;
    """

    return execute_select_query(query)