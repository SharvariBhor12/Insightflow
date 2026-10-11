import json
from typing import Annotated, TypedDict

import pandas as pd
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from agents.agent_tools import build_tools
from tools.data_tools import profile_dataset
from utils.llm import get_llm

PLANNER_PROMPT = """You are the planning step of a data analyst agent.
Given a dataset profile and a user question, write a short numbered plan
(3 to 6 steps) for the analysis. Each step should say what to compute or check
and which kind of tool fits (SQL, Pandas, period comparison, anomaly detection, chart).
For "why" questions, plan to measure the change first, then break it down
by dimensions such as product, category, and region.
Do not compute anything and do not state any numbers. Output only the numbered plan."""

SYSTEM_PROMPT = """You are InsightFlow, a careful data analyst.
You answer questions about a dataset by calling tools. Never guess numbers:
every number in your answer must come from a tool result.
Follow the plan below, but adapt it if the results show something unexpected.
If a tool returns an ERROR, read it, fix your input, and try again.
Do not assume currency or units that are not in the data; write plain numbers.
Give a clear, short answer based only on the evidence you collected."""


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]  # new messages are appended
    plan: str  # written by the planner node, read by the agent node


def build_agent(df: pd.DataFrame):
    """Build the LangGraph agent. Returns (compiled_graph, charts_list)."""
    tools, charts = build_tools(df)
    llm = get_llm()
    llm_with_tools = llm.bind_tools(tools)
    profile_text = json.dumps(profile_dataset(df), default=str)[:3000]

    def planner_node(state: AgentState):
        question = state["messages"][-1].content
        prompt = f"Dataset profile:\n{profile_text}\n\nUser question: {question}"
        response = llm.invoke([SystemMessage(PLANNER_PROMPT), HumanMessage(prompt)])
        return {"plan": response.text}

    def agent_node(state: AgentState):
        system = SYSTEM_PROMPT + "\n\nPLAN:\n" + state.get("plan", "")
        messages = [SystemMessage(system)] + state["messages"]
        return {"messages": [llm_with_tools.invoke(messages)]}

    graph = StateGraph(AgentState)
    graph.add_node("planner", planner_node)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(tools))

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "agent")
    graph.add_conditional_edges("agent", tools_condition)  # tool requested -> "tools", else END
    graph.add_edge("tools", "agent")

    return graph.compile(), charts


def run_agent(df: pd.DataFrame, question: str):
    """Run the agent. Returns (final_answer, all_messages, charts, plan)."""
    app, charts = build_agent(df)
    result = app.invoke(
        {"messages": [HumanMessage(question)], "plan": ""},
        config={"recursion_limit": 25},  # safety cap against runaway loops
    )
    messages = result["messages"]
    return messages[-1].text, messages, charts, result["plan"]