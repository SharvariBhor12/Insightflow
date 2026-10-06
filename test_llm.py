from utils.llm import ask_llm

system = "You are a concise data analyst. Answer in one sentence."
answer = ask_llm("What does it mean when revenue drops 18% quarter over quarter?", system)
print(answer)