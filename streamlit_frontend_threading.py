import streamlit as st
import uuid
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage

# ---------------- CONFIG ----------------
def generate_thread_id():
    """Generate unique thread IDs"""
    return f"thread-{uuid.uuid4().hex[:8]}"

# Initialize session state
if "threads" not in st.session_state:
    st.session_state["threads"] = {}  # dict {thread_id: message_history}
if "current_thread" not in st.session_state:
    # Start with one thread
    new_thread = generate_thread_id()
    st.session_state["current_thread"] = new_thread
    st.session_state["threads"][new_thread] = []

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("💬 Chat App")
    st.markdown("### My Conversations")

    # Display all thread IDs as clickable buttons
    for thread_id in st.session_state["threads"].keys():
        if st.button(thread_id, key=thread_id):
            st.session_state["current_thread"] = thread_id

    st.markdown("---")
    st.markdown(f"**Current Thread:** `{st.session_state['current_thread']}`")

    # Start new chat button
    if st.button("➕ New Chat"):
        new_thread = generate_thread_id()
        st.session_state["current_thread"] = new_thread
        st.session_state["threads"][new_thread] = []

# ---------------- MAIN CHAT WINDOW ----------------
current_thread = st.session_state["current_thread"]
message_history = st.session_state["threads"][current_thread]

# Display chat history
for message in message_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
user_input = st.chat_input("Type here...")

if user_input:
    # Save user message
    message_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Prepare config for this thread
    CONFIG = {"configurable": {"thread_id": current_thread}}

    # Stream AI response
    with st.chat_message("assistant"):
        response_stream = chatbot.stream(
            {"messages": [HumanMessage(content=user_input)]},
            config=CONFIG,
            stream_mode="messages"
        )

        full_reply = ""
        message_placeholder = st.empty()

        for message_chunk, _ in response_stream:
            if hasattr(message_chunk, "content") and message_chunk.content:
                chunk_text = message_chunk.content
                full_reply += chunk_text
                message_placeholder.markdown(full_reply + "▌")  # live typing effect

        # Finalize reply (remove cursor)
        message_placeholder.markdown(full_reply)

# ✅ Save only once (don’t re-display!)
    message_history.append({"role": "assistant", "content": full_reply})




