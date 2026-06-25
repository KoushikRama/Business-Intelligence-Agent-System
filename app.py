import streamlit as st
import time

from graph.bi_graph import run_graph
from memory.conversation_store import (
    create_conversation,
    get_conversations_by_employee,
    get_messages_by_conversation,
    update_conversation_title,
    delete_conversation,
    get_employee,
    save_message,
)

DEMO_EMPLOYEE_ID = "859a6ee7-b0a0-44b6-a35f-efe7c370c504"


def load_conversation(conversation_id: str):
    st.session_state.conversation_id = conversation_id

    db_messages = get_messages_by_conversation(conversation_id)

    st.session_state.messages = [
        {
            "role": msg["role"],
            "content": msg["message_text"],
        }
        for msg in db_messages
    ]


def type_assistant_message(message: str, delay: float = 0.001):
    placeholder = st.empty()
    typed_text = ""

    for char in message:
        typed_text += char
        placeholder.markdown(typed_text)
        time.sleep(delay)


def get_greeting_message(employee):
    first_name = employee["first_name"].split()[0]

    return f"""
Hello {first_name}! I'm your NovaCart Business Intelligence Assistant. 

I can help you analyze business data, answer questions about company policies, and investigate operational issues. How can I help you today?
"""


st.set_page_config(
    page_title="NovaCart BI Assistant",
    page_icon="📊",
    layout="wide",
)

st.title("📊 NovaCart Business Intelligence Assistant")

if "employee_id" not in st.session_state:
    st.session_state.employee_id = DEMO_EMPLOYEE_ID

if "typing_greeting" not in st.session_state:
    st.session_state.typing_greeting = False

employee_id = st.session_state.employee_id
employee = get_employee(employee_id)

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = create_conversation(
        st.session_state.employee_id,
        title="New Conversation",
    )

if "messages" not in st.session_state:
    load_conversation(st.session_state.conversation_id)


query_params = st.query_params

if "conversation_id" in query_params:
    selected_conversation_id = query_params["conversation_id"]

    if selected_conversation_id != str(st.session_state.conversation_id):
        load_conversation(selected_conversation_id)
        st.session_state.typing_greeting = False


with st.sidebar:
    st.title("📊 NovaCart BI")
    st.caption("Enterprise Assistant")

    # ---------------- New Conversation ---------------- #

    if st.button("➕ New Conversation", use_container_width=True):
        new_conversation_id = create_conversation(
            st.session_state.employee_id,
            title="New Conversation",
        )

        save_message(
            conversation_id=new_conversation_id,
            role="assistant",
            message=get_greeting_message(employee),
        )

        load_conversation(new_conversation_id)

        st.session_state.typing_greeting = True
        st.query_params["conversation_id"] = str(new_conversation_id)

        st.rerun()

    st.divider()

    # ---------------- Employee ---------------- #

    st.markdown(
        f"""
**👤 {employee["first_name"]} {employee["last_name"]}**  
{employee["job_role"]}
"""
    )

    # ---------------- Conversations ---------------- #

    conversations = get_conversations_by_employee(
        st.session_state.employee_id
    )

    conversation_ids = [
        str(conv["conversation_id"])
        for conv in conversations
    ]

    current_index = next(
        (
            i
            for i, conv in enumerate(conversations)
            if str(conv["conversation_id"]) == str(st.session_state.conversation_id)
        ),
        0,
    )

    selected_conversation_id = st.selectbox(
        "Conversations",
        conversation_ids,
        index=current_index,
        format_func=lambda cid: next(
            conv["title"]
            for conv in conversations
            if str(conv["conversation_id"]) == cid
        ),
    )

    if selected_conversation_id != str(st.session_state.conversation_id):
        load_conversation(selected_conversation_id)

        st.session_state.typing_greeting = False
        st.query_params["conversation_id"] = selected_conversation_id

        st.rerun()

    st.divider()

    # ---------------- Conversation Details ---------------- #

    current_conv = next(
        conv
        for conv in conversations
        if str(conv["conversation_id"]) == str(st.session_state.conversation_id)
    )

    st.subheader("Conversation Details")

    new_title = st.text_input(
        "Rename",
        value=current_conv["title"],
    )

    if st.button("Save Title", use_container_width=True):
        update_conversation_title(
            st.session_state.conversation_id,
            new_title,
        )
        st.rerun()

    if st.button(
        "🗑 Delete Conversation",
        use_container_width=True,
    ):
        delete_conversation(st.session_state.conversation_id)

        remaining_conversations = get_conversations_by_employee(
            st.session_state.employee_id
        )

        if remaining_conversations:
            next_conversation_id = str(
                remaining_conversations[0]["conversation_id"]
            )

            load_conversation(next_conversation_id)

            st.session_state.typing_greeting = False
            st.query_params["conversation_id"] = next_conversation_id

        else:
            new_conversation_id = create_conversation(
                st.session_state.employee_id,
                title="New Conversation",
            )

            save_message(
                conversation_id=new_conversation_id,
                role="assistant",
                message=get_greeting_message(employee),
            )

            load_conversation(new_conversation_id)

            st.session_state.typing_greeting = True
            st.query_params["conversation_id"] = str(new_conversation_id)

        st.rerun()


# ---------------- Display Messages ---------------- #

for index, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        should_type_greeting = (
            st.session_state.typing_greeting
            and message["role"] == "assistant"
            and index == len(st.session_state.messages) - 1
        )

        if should_type_greeting:
            type_assistant_message(message["content"])
            st.session_state.typing_greeting = False
        else:
            st.markdown(message["content"])


# ---------------- Chat Input ---------------- #

user_question = st.chat_input("Ask a business question...")

if user_question:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_question,
        }
    )

    with st.chat_message("user"):
        st.markdown(user_question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = run_graph(
                question=user_question,
                conversation_id=st.session_state.conversation_id,
            )

        st.markdown(response)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response,
        }
    )