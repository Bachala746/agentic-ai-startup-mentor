from langgraph.graph import StateGraph, START, END

from .state import StartupState
from .market_agent import market_agent
from .finance_agent import finance_agent
from .risk_agent import risk_agent
from .decision_agent import decision_agent


# Create the LangGraph workflow
builder = StateGraph(StartupState)


# Add the four agents as graph nodes
builder.add_node("market_agent", market_agent)
builder.add_node("finance_agent", finance_agent)
builder.add_node("risk_agent", risk_agent)
builder.add_node("decision_agent", decision_agent)


# Connect the agents in sequence
builder.add_edge(START, "market_agent")
builder.add_edge("market_agent", "finance_agent")
builder.add_edge("finance_agent", "risk_agent")
builder.add_edge("risk_agent", "decision_agent")
builder.add_edge("decision_agent", END)


# Compile the graph
startup_graph = builder.compile()