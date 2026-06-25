import uuid

from database.queries import execute_insert_query, execute_select_query

def get_employee(employee_id: str):
    query = f"""
    SELECT
        employee_id,
        first_name,
        last_name,
        email,
        department,
        job_role,
        access_level
    FROM employees
    WHERE employee_id = '{employee_id}';
    """

    result = execute_select_query(query)

    return result[0] if result else None

def create_conversation(employee_id: str, title: str = "New Conversation"):
    conversation_id = str(uuid.uuid4())
    safe_title = title.replace("'", "''")

    query = f"""
    INSERT INTO conversations(conversation_id, employee_id, title)
    VALUES ('{conversation_id}', '{employee_id}', '{safe_title}');
    """

    execute_insert_query(query)
    return conversation_id

def get_conversations_by_employee(employee_id: str):
    query = f"""
    SELECT conversation_id, title, created_at
    FROM conversations
    WHERE employee_id = '{employee_id}'
    ORDER BY created_at DESC;
    """
    return execute_select_query(query)


def update_conversation_title(conversation_id: str, title: str):
    safe_title = title.replace("'", "''")

    query = f"""
    UPDATE conversations
    SET title = '{safe_title}'
    WHERE conversation_id = '{conversation_id}';
    """

    execute_insert_query(query)

def get_messages_by_conversation(conversation_id:str):
    query = f"""
SELECT role, message_text
FROM messages
WHERE conversation_id = '{conversation_id}'
ORDER BY created_at ASC
"""
    return execute_select_query(query)

def delete_conversation(conversation_id: str):
    query = f"""
    DELETE FROM conversations
    WHERE conversation_id = '{conversation_id}';
    """
    execute_insert_query(query)


def save_message(conversation_id: str, role: str, message: str) -> str:
    message_id = str(uuid.uuid4())

    cleaned_message = message.replace("'", "''")

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
        '{cleaned_message}'
    );
    """

    execute_insert_query(query)

    return message_id


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