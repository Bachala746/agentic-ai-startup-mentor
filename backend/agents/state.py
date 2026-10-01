from typing import TypedDict


class StartupState(TypedDict, total=False):
    startup_idea: str
    founder_profile: dict | None
    mentor: str

    web_sources: list[dict]
    financial_web_sources: list[dict]
    risk_web_sources: list[dict]

    market_analysis: dict
    financial_analysis: dict
    risk_analysis: dict
    final_recommendation: str
    roadmap: list[str]