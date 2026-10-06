import json

from utils.llm import ask_llm

SYSTEM_PROMPT = """You are a careful data analyst.
You are given a summary (profile) of a dataset and a user question.
Answer using only the information provided. If the answer cannot be
determined from the profile, say so clearly instead of guessing."""


def simple_answer(question: str, profile: dict) -> str:
    """Plain LLM answer: the model sees only the profile, not the raw data."""
    prompt = (
        f"Dataset profile:\n{json.dumps(profile, indent=2, default=str)}\n\n"
        f"Question: {question}"
    )
    return ask_llm(prompt, SYSTEM_PROMPT)