from langgraph.graph import StateGraph, START, END

from .state import StartupState
from .market_agent import market_agent
from .finance_agent import finance_agent
from .risk_agent import risk_agent
from .decision_agent import decision_agent
from .startup_intelligence_agent import startup_intelligence_agent


builder = StateGraph(StartupState)

builder.add_node("market_agent", market_agent)
builder.add_node("finance_agent", finance_agent)
builder.add_node("risk_agent", risk_agent)
builder.add_node("decision_agent", decision_agent)
builder.add_node("startup_intelligence_agent", startup_intelligence_agent)

builder.add_edge(START, "market_agent")
builder.add_edge("market_agent", "finance_agent")
builder.add_edge("finance_agent", "risk_agent")
builder.add_edge("risk_agent", "decision_agent")
builder.add_edge("decision_agent", "startup_intelligence_agent")
builder.add_edge("startup_intelligence_agent", END)

startup_graph = builder.compile()