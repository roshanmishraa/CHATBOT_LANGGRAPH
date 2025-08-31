from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
import os

# Load API key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("❌ GOOGLE_API_KEY not found in .env file")

print("✅ Loaded API Key")

# Config required by LangGraph checkpointer (thread/session id)
CONFIG = {
    "configurable": {
        "thread_id": "thread-1"
    }
}

# Gemini 2.5 Pro LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro",
    google_api_key=api_key
)

# Define conversation state
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# Node function
def chat_node(state: ChatState):
    messages = state.get("messages", [])
    
    if not messages:
        messages = [HumanMessage(content="Hello!")]

    print(f"📩 User said: {messages[-1].content}")

    try:
        response = llm.invoke(messages)
        ai_text = getattr(response, "content", "🤖 Sorry, no response.")
    except Exception as e:
        ai_text = f"⚠️ Error: {str(e)}"

    print(f"🤖 Gemini replied: {ai_text}")
    return {"messages": [AIMessage(content=ai_text)]}

# Checkpointer (stores history in memory)
checkpointer = InMemorySaver()

# Graph workflow
graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

# Compile chatbot
chatbot = graph.compile(checkpointer=checkpointer)
print("✅ Chatbot compiled successfully!")

# Standalone test
if __name__ == "__main__":
    test_response = chatbot.invoke(
        {"messages": [HumanMessage(content="Hello Gemini!")]},
        config=CONFIG
    )





