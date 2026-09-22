from typing import TypedDict


class StartupState(TypedDict, total=False):
    startup_idea: str
    founder_profile: dict | None
    mentor: str

    market_analysis: dict
    financial_analysis: dict
    risk_analysis: dict

    final_recommendation: str
    roadmap: list[str]