from typing import Annotated, TypedDict

import pandas as pd
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from agents.agent_tools import build_tools
from utils.llm import get_llm

SYSTEM_PROMPT = """You are InsightFlow, a careful data analyst.
You answer questions about a sales dataset by calling tools. Never guess numbers:
every number in your answer must come from a tool result.
If a tool returns an ERROR, read it, fix your input, and try again.
When you have enough evidence, give a clear, short answer."""


class AgentState(TypedDict):
    # add_messages means new messages are appended to the list, not replaced
    messages: Annotated[list, add_messages]


def build_agent(df: pd.DataFrame):
    """Build the LangGraph agent. Returns (compiled_graph, charts_list)."""
    tools, charts = build_tools(df)
    llm_with_tools = get_llm().bind_tools(tools)

    def agent_node(state: AgentState):
        messages = [SystemMessage(SYSTEM_PROMPT)] + state["messages"]
        return {"messages": [llm_with_tools.invoke(messages)]}

    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(tools))

    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", tools_condition)  # tool requested -> "tools", else END
    graph.add_edge("tools", "agent")

    return graph.compile(), charts


def run_agent(df: pd.DataFrame, question: str):
    """Run the agent on a question. Returns (final_answer, all_messages, charts)."""
    app, charts = build_agent(df)
    result = app.invoke(
        {"messages": [HumanMessage(question)]},
        config={"recursion_limit": 15},  # safety: stop runaway loops
    )
    messages = result["messages"]
    return messages[-1].text, messages, charts