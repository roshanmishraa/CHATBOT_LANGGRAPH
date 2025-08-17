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
print("Loaded API Key:", api_key)

# Config required by LangGraph checkpointer
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

# Conversation state
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# Node function
def chat_node(state: ChatState):
    # Flatten messages to a single list of BaseMessage
    flat_messages = []
    for m in state['messages']:
        if isinstance(m, (list, tuple)):
            for x in m:
                if isinstance(x, BaseMessage):
                    flat_messages.append(x)
        elif isinstance(m, BaseMessage):
            flat_messages.append(m)

    # Default message if empty
    if not flat_messages:
        flat_messages = [HumanMessage(content="Hello!")]

    # Call Gemini 2.5 Pro
    response = llm.generate(flat_messages)

    # Safely extract text
    ai_text = response.generations[0][0].text if response.generations else "🤖 Sorry, no response."

    # Return as AIMessage list
    return {"messages": [AIMessage(content=ai_text)]}

# Checkpointer
checkpointer = InMemorySaver()

# Graph workflow
graph = StateGraph(ChatState, config=CONFIG)  # <-- Pass CONFIG here
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

# Compile chatbot with checkpointer
chatbot = graph.compile(checkpointer=checkpointer)
print("Chatbot compiled successfully!")

# Standalone test
if __name__ == "__main__":
    test_response = chatbot.invoke(
        {"messages": [HumanMessage(content="Hello Gemini!") ]},
        config=CONFIG  # <-- Pass CONFIG here too
    )
    print("Response:", test_response["messages"][-1].content)

