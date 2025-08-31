import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage

CONFIG = {"configurable": {"thread_id": "thread-1"}}

# Initialize session state
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

# Display chat history
for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input box
user_input = st.chat_input("Type here...")

if user_input:
    # Save user message
    st.session_state["message_history"].append(
        {"role": "user", "content": user_input}
    )
    with st.chat_message("user"):
        st.markdown(user_input)

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

    # Save assistant reply
    st.session_state["message_history"].append(
        {"role": "assistant", "content": full_reply}
    )

