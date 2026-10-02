import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from ddgs import DDGS

from .state import StartupState


load_dotenv()


class RiskAnalysis(BaseModel):
    market_risks: list[str] = Field(
        description="Important market-related risks"
    )
    financial_risks: list[str] = Field(
        description="Important financial risks"
    )
    product_technical_risks: list[str] = Field(
        description="Product and technical risks"
    )
    customer_adoption_risks: list[str] = Field(
        description="Customer and adoption risks"
    )
    implementation_challenges: list[str] = Field(
        description="Possible implementation challenges"
    )
    mitigation_strategies: list[str] = Field(
        description="Practical ways to reduce the identified risks"
    )


llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.2,
)

structured_llm = llm.with_structured_output(RiskAnalysis)


def risk_agent(state: StartupState):
    startup_idea = state["startup_idea"]
    founder_profile = state.get("founder_profile") or {}
    market_analysis = state.get("market_analysis") or {}
    financial_analysis = state.get("financial_analysis") or {}

    # -----------------------------------------
    # Dynamic Risk Web Search
    # -----------------------------------------

    queries = [
        {
            "category": "Technical and Operational Risks",
            "queries": [
                f"{startup_idea} technical risks",
                f"{startup_idea} operational risks",
            ],
        },
        {
            "category": "Security and Privacy Risks",
            "queries": [
                f"{startup_idea} security risks",
                f"{startup_idea} privacy risks",
            ],
        },
        {
            "category": "Legal and Regulatory Risks",
            "queries": [
                f"{startup_idea} legal risks",
                f"{startup_idea} regulations",
            ],
        },
    ]

    web_results = []

    for search in queries:
        category = search["category"]

        for query in search["queries"]:
            try:
                results = DDGS().text(
                    query,
                    max_results=5
                )

                for result in results:
                    web_results.append(
                        {
                            "category": category,
                            "title": result.get("title", ""),
                            "url": result.get("href", ""),
                            "snippet": result.get("body", ""),
                        }
                    )

            except Exception as error:
                print(
                    f"Risk web search failed for '{query}': {error}"
                )

    # Remove duplicate URLs
    unique_results = []
    seen_urls = set()

    for result in web_results:
        url = result.get("url", "")

        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_results.append(result)

    # Keep maximum 15 sources
    risk_keywords = [
        "risk",
        "security",
        "privacy",
        "cybersecurity",
        "data protection",
        "legal",
        "regulation",
        "compliance",
        "vulnerability",
        "threat",
        "breach",
        "fraud",
        "operational",
        "technical",
    ]

    filtered_results = []

    for result in unique_results:
        text = (
            f"{result.get('title', '')} "
            f"{result.get('snippet', '')}"
        ).lower()

        risk_matches = sum(
            1 for keyword in risk_keywords
            if keyword in text
        )

        if risk_matches >= 1:
            result["relevance_score"] = risk_matches
            filtered_results.append(result)

    filtered_results.sort(
        key=lambda x: x.get("relevance_score", 0),
        reverse=True
    )

    web_results = filtered_results[:5]

    for result in web_results:
        result.pop("relevance_score", None)

    print(f"Risk web results: {len(web_results)}")

    # -----------------------------------------
    # Risk AI Analysis
    # -----------------------------------------

    prompt = f"""
You are the Risk Agent in an AI Personalized Startup Mentor.

Analyze the risks and challenges of the startup using the startup
information and current web research provided below.

Startup Idea:
{startup_idea}

Founder Profile:
{founder_profile}

Market Agent Analysis:
{market_analysis}

Finance Agent Analysis:
{financial_analysis}

Current Risk Web Research:
{web_results}

Analyze:

1. Market risks
2. Financial risks
3. Product and technical risks
4. Customer/adoption risks
5. Implementation challenges
6. Practical mitigation strategies

Use the web research when it is relevant to the startup.

Personalize the analysis using the founder's:
- Skills
- Experience
- Budget
- Goals

Important rules:

- Do not invent precise statistics or unsupported facts.
- Do not present guesses as real facts.
- Use the provided web research as supporting information.
- If the web research does not provide enough evidence, give a
  practical general risk analysis instead of inventing facts.
- Keep the analysis practical and easy to understand.
"""

    result = structured_llm.invoke(prompt)

    return {
        "risk_analysis": result.model_dump(),
        "risk_web_sources": web_results,
    }