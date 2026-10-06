import os
from dotenv import load_dotenv

load_dotenv()

import streamlit, pandas, langgraph

print("Streamlit:", streamlit.__version__)
print("Pandas:", pandas.__version__)
print("LangGraph imported OK")
print("API key loaded:", bool(os.getenv("GOOGLE_API_KEY")))

from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(model="gemini-3.8-flash")
reply = llm.invoke("Say hello in five words.")
print("LLM reply:", reply.content)