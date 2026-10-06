import os
import time

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# Change the model name here only. Every other file imports from this module.
MODEL_NAME = "gemini-3.8-flash"


class LLMError(Exception):
    """Raised when the LLM cannot be reached after retries."""


def get_llm(temperature: float = 0.0) -> ChatGoogleGenerativeAI:
    """Create the LLM client. Temperature 0 = most consistent answers."""
    if not os.getenv("GOOGLE_API_KEY"):
        raise LLMError("GOOGLE_API_KEY is missing. Add it to your .env file.")
    return ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=temperature)


def ask_llm(prompt: str, system_prompt: str = "", retries: int = 3) -> str:
    """Send a prompt, retry on temporary failures, return clean text."""
    llm = get_llm()
    messages = []
    if system_prompt:
        messages.append(("system", system_prompt))
    messages.append(("human", prompt))

    last_error = None
    for attempt in range(retries):
        try:
            response = llm.invoke(messages)
            return response.text
        except Exception as e:
            last_error = e
            message = str(e)
            temporary = "503" in message or "429" in message or "UNAVAILABLE" in message
            if not temporary:
                break  # real error (bad key, bad model), retrying won't help
            time.sleep(2 ** attempt)  # wait 1s, 2s, 4s

    raise LLMError(f"LLM call failed: {last_error}")