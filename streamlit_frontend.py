import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage

# Fixed thread id
CONFIG = {'configurable': {'thread_id': 'thread-1'}}

# Initialize session message history
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

# Display previous messages
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

# Input box
user_input = st.chat_input("Type here...")

if user_input:
    # Save and display user message
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    # Call backend chatbot safely
    response = chatbot.invoke({"messages": [HumanMessage(content=user_input)]}, config=CONFIG)

    # Safe extraction of AI response
    ai_messages = response.get('messages', [])
    if ai_messages and hasattr(ai_messages[-1], 'content'):
        ai_message = ai_messages[-1].content
    else:
        ai_message = "🤖 Sorry, I couldn't generate a response."

    # Save and display AI response
    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
    with st.chat_message('assistant'):
        st.text(ai_message)

