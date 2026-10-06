import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field, model_validator
from langchain_google_genai import ChatGoogleGenerativeAI

try:
    from duckduckgo_search import DDGS
except ImportError:
    from ddgs import DDGS

from .state import StartupState

load_dotenv()


# ============================================================================
# PYDANTIC SCHEMAS FOR STRUCTURED INTELLIGENCE
# ============================================================================

class FundingOpportunity(BaseModel):
    name: str = Field(default="", description="Funding program or scheme name")
    organization: str = Field(default="", description="Ministry, government body, corporation, VC, or accelerator providing the program")
    funding_type: str = Field(
        default="Grant",
        description="Type: Grant, Equity Investment, Debt, Accelerator Funding, Corporate Program, Credit/Support, Other"
    )
    funding_amount: str = Field(default="Not verified", description="Verified monetary funding amount, grant value, or credits")
    eligibility: str = Field(default="Not verified", description="Key eligibility criteria")
    who_can_apply: str = Field(default="Not verified", description="Applicant criteria, entity stage, or incorporation requirements")
    startup_stage: str = Field(default="Not verified", description="Ideation, Validation, MVP, Early Traction, Scaling")
    usage: str = Field(default="Not verified", description="Permitted use of funds or credit resources")
    where_to_apply: str = Field(default="Not verified", description="Official department, agency, or portal name")
    application_website: str = Field(
        default="Not verified",
        description="Direct official portal URL for applications. If not verified, state 'Not verified'"
    )
    application_steps: list[str] = Field(default_factory=list, description="Step-by-step application instructions")
    required_documents: list[str] = Field(default_factory=list, description="List of officially required documents")
    deadline: str = Field(default="Not verified", description="Application deadline or 'Ongoing' / 'Not verified'")
    official_source_name: str = Field(
        default="Not verified",
        description="Name of the official government ministry, organizing body, or company (NEVER a third-party blog)"
    )
    official_source_url: str = Field(
        default="Not verified",
        description="Official root or scheme URL from the organizing body. If unverified, state 'Not verified'"
    )
    official_source: str = Field(
        default="",
        description="Backward-compatible display name for the official source"
    )
    why_suitable: str = Field(default="", description="Why this opportunity aligns directly with this specific startup idea")


class TeamRole(BaseModel):
    role: str = Field(default="", description="Role title")
    reports_to: str = Field(default="Founder/CEO", description="Supervisor in team hierarchy")
    responsibilities: str = Field(default="", description="Core duties and ownership areas")
    why_needed: str = Field(default="", description="Specific justification for this startup")
    skills: list[str] = Field(default_factory=list, description="Required competencies and technical skills")
    priority: str = Field(default="Essential", description="'Essential' for launch/MVP or 'Later' for scaling")


class HierarchyNode(BaseModel):
    role: str = Field(default="", description="Role title in the hierarchy tree")
    reports_to: str = Field(default="", description="Direct supervisor role (blank for top Founder/CEO)")


class Competitor(BaseModel):
    name: str = Field(default="", description="Real competitor company or product name")
    product_service: str = Field(default="", description="Core product or service offering")
    target_customers: str = Field(default="", description="Target customer segments")
    business_model: str = Field(default="", description="Monetization model")
    pricing: str = Field(default="Not publicly verified", description="Verified pricing tiers or structure")
    strengths: list[str] = Field(default_factory=list, description="Key competitor advantages")
    weaknesses: list[str] = Field(default_factory=list, description="Identified competitor market gaps or weaknesses")
    funding_raised: str = Field(
        default="Not publicly verified",
        description="Total verified external funding/investment raised (e.g. '$16M across Series A'). Do NOT label as revenue!"
    )
    revenue: str = Field(
        default="Not publicly verified",
        description="Verified revenue with financial year and source (e.g. '₹45 Cr (FY 2023) - MCA Filing'). NEVER classify investment/funding raised as revenue!"
    )
    profit_loss: str = Field(
        default="Not publicly verified",
        description="Verified profit/loss with financial year and source, or 'Not publicly verified'"
    )
    source: str = Field(default="", description="Source for financial/company data (e.g. MCA filing, Tracxn, Annual Report)")


class SourceItem(BaseModel):
    name: str = Field(default="", description="Descriptive name of the source (e.g. 'BIRAC Official Portal', 'Qure.ai')")
    url: str = Field(default="", description="Verified working URL from web research")
    source_type: str = Field(
        default="Official Government/Organization Source",
        description="Type: 'Official Government/Organization Source', 'Company Source', 'Financial Source', or 'Supporting / Reference Source'"
    )
    category: str = Field(default="Official", description="'Official' or 'Supporting'")


class RoadmapStep(BaseModel):
    step_number: int = Field(default=1, description="Sequential phase number")
    phase_name: str = Field(default="", description="Phase title tailored to this startup idea")
    description: str = Field(default="", description="Specific execution milestones and objectives to accomplish")
    estimated_timeline: str = Field(default="", description="Estimated duration (e.g. 'Months 1-2')")


class StartupIntelligenceReport(BaseModel):
    executive_summary: str = Field(default="", description="Executive summary of intelligence findings")
    government_funding_schemes: list[FundingOpportunity] = Field(
        default_factory=list,
        description="Government grants, startup schemes, seed funds, institutional loans, and official incubator programs"
    )
    private_funding_opportunities: list[FundingOpportunity] = Field(
        default_factory=list,
        description="Private programs, VC funding, corporate grants, angel networks, accelerators, and corporate credits"
    )
    funding_opportunities: list[FundingOpportunity] = Field(
        default_factory=list,
        description="Consolidated list of all funding opportunities for backward compatibility"
    )
    recommended_team_structure: list[TeamRole] = Field(default_factory=list)
    team_hierarchy: list[HierarchyNode] = Field(default_factory=list)
    competitor_analysis: list[Competitor] = Field(default_factory=list)
    financial_information: list[str] = Field(default_factory=list)
    startup_vs_competitors: list[str] = Field(default_factory=list)
    important_recommendations: list[str] = Field(default_factory=list)
    sources: list[SourceItem] = Field(default_factory=list)
    roadmap: list[RoadmapStep] = Field(
        default_factory=list,
        description="Sequential 5 to 7 phase execution roadmap tailored to the startup idea"
    )

    @model_validator(mode="after")
    def sync_and_validate_report(self):
        # 1. Ensure funding_opportunities contains both categories for backward compatibility
        if not self.funding_opportunities:
            self.funding_opportunities = self.government_funding_schemes + self.private_funding_opportunities

        # 2. Ensure official_source display fallback is populated
        for opp in self.government_funding_schemes + self.private_funding_opportunities + self.funding_opportunities:
            if not opp.official_source or opp.official_source == "Not verified":
                if opp.official_source_name and opp.official_source_name != "Not verified":
                    opp.official_source = opp.official_source_name
                elif opp.organization and opp.organization != "Not verified":
                    opp.official_source = opp.organization

        return self


# ============================================================================
# LLM SETUP
# ============================================================================

model_name = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

llm = ChatGoogleGenerativeAI(
    model=model_name,
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.2,
)

structured_llm = llm.with_structured_output(StartupIntelligenceReport)


# ============================================================================
# SEARCH FUNCTIONALITY
# ============================================================================

def search_intelligence_information(startup_idea: str) -> list[dict]:
    queries = [
        f"{startup_idea} government funding schemes grants seed fund India official portal",
        f"{startup_idea} private accelerators venture capital angel network corporate grants India",
        f"{startup_idea} competitor companies products business model India",
        f"{startup_idea} competitors funding raised revenue financial filings",
        f"{startup_idea} startup grants eligibility official application portal",
    ]

    results = []

    for query in queries:
        try:
            search_results = DDGS().text(query, max_results=5)
            if search_results:
                for item in search_results:
                    url = item.get("href", "").strip()
                    if url:
                        results.append({
                            "title": item.get("title", "").strip(),
                            "url": url,
                            "snippet": item.get("body", "").strip(),
                        })
        except Exception as error:
            print(f"Intelligence search warning for query '{query}': {error}")

    # Deduplicate results by URL
    unique = []
    seen = set()

    for result in results:
        if result["url"] not in seen:
            seen.add(result["url"])
            unique.append(result)

    return unique[:25]


# ============================================================================
# AGENT NODE
# ============================================================================

def startup_intelligence_agent(state: StartupState) -> dict:
    startup_idea = state.get("startup_idea", "")
    founder_profile = state.get("founder_profile") or {}

    web_results = search_intelligence_information(startup_idea)

    web_information = "\n\n".join(
        f"SOURCE:\n"
        f"Title: {item['title']}\n"
        f"URL: {item['url']}\n"
        f"Information: {item['snippet']}"
        for item in web_results
    ) if web_results else "No live web results available."

    prompt = f"""
You are the Startup Intelligence Agent.

Analyze the given startup idea using the user founder profile and the CURRENT web research findings.

STARTUP IDEA:
{startup_idea}

FOUNDER PROFILE:
{founder_profile}

CURRENT WEB RESEARCH:
{web_information}

Generate a comprehensive, strictly accurate Startup Intelligence Report adhering to the following rules:

1. EXECUTIVE SUMMARY:
   Provide a concise overview of the funding landscape, competitive dynamics, and operational pathway for this startup.

2. FUNDING CATEGORIES (MUST BE SEPARATED):
   A. GOVERNMENT FUNDING SCHEMES (government_funding_schemes):
      - Identify genuine government grants, startup schemes, seed funds (e.g. SISFS, BIRAC BIG, NIDHI-PRAYAS, MeitY TIDE, PMEGP, CGTMSE), government loans, or public incubators.
      - For each, provide: name, organization, funding_type, funding_amount, eligibility, who_can_apply, startup_stage, usage, where_to_apply, application_website, application_steps, required_documents, deadline, official_source_name, official_source_url, and why_suitable.

   B. PRIVATE FUNDING OPPORTUNITIES (private_funding_opportunities):
      - Identify genuine private funding programs, corporate accelerator programs, angel networks, VC seed programs, or corporate credits (e.g., Google for Startups, AWS Activate, Techstars, Y Combinator, Indian Angel Network, corporate innovation challenges).
      - Clearly identify the actual funding/support type: Grant, Equity Investment, Debt, Accelerator Funding, Corporate Program, Credit/Support, or Other.
      - For each, provide the same comprehensive fields listed above.

3. CRITICAL SOURCE LOGIC & VERIFICATION RULES:
   - For every funding opportunity:
     * official_source_name: Must be the ACTUAL government ministry/body or the company/VC running the program (e.g. 'Biotechnology Industry Research Assistance Council (BIRAC)', 'Startup India', 'Microsoft for Startups').
     * official_source_url: Must be the actual verified official website URL (e.g. 'https://birac.nic.in/').
     * application_website: Must be the actual verified official portal/page to apply.
   - ABSOLUTE RULE: NEVER call a third-party blog, news aggregator, or consultancy article (e.g., Incorpx, Medium, generic blogs) an 'Official Source'.
   - If an official source name or URL cannot be verified from the web research:
     Set official_source_name = 'Not verified'
     Set official_source_url = 'Not verified'
     Set application_website = 'Not verified'
   - NEVER invent or hallucinate URLs. Third-party articles may only be used as supporting references.

4. COMPANY & TEAM STRUCTURE:
   - Recommend startup-specific roles tailored to this business model with priority ('Essential' vs 'Later').
   - In each role, set 'reports_to' to indicate hierarchy.
   - Populate 'team_hierarchy' with node pairs (role and reports_to). The root role (e.g. Founder/CEO) has reports_to = "".

5. COMPETITOR ANALYSIS & FINANCIAL CLASSIFICATION (CRITICAL):
   - Identify real competitors or market alternatives.
   - STRICT FINANCIAL ACCURACY RULE:
     * NEVER classify external funding or investment raised as company revenue!
     * Example: If a competitor secured $16M in funding, record:
       funding_raised: "$16M funding secured"
       revenue: "Not publicly verified"
     * Revenue and profit/loss must ONLY reflect actual business operating earnings.
     * If historical verified revenue exists, cite the exact financial year and source (e.g. '₹45 Cr (FY 2023) - MCA Filing'). Otherwise, state 'Not publicly verified'.

6. FINANCIAL INFORMATION:
   - Provide industry financial benchmarks, standard margins, CAC/LTV standards, or unit economics with referenced year and source.

7. STARTUP VS COMPETITORS:
   - Clear, practical comparison points highlighting advantages and differentiators.

8. IMPORTANT RECOMMENDATIONS:
   - Actionable, prioritized recommendations for the founder.

9. SOURCES / OFFICIAL LINKS (sources):
   - Provide the key sources supporting the report. Each source must have:
     * name: Clear descriptive name (e.g. 'BIRAC Official Portal', 'Qure.ai Official Website')
     * url: Clickable verified URL
     * source_type: 'Official Government/Organization Source', 'Company Source', 'Financial Source', or 'Supporting / Reference Source'
     * category: 'Official' or 'Supporting'
   - Third-party blogs and articles must strictly be classified as 'Supporting / Reference Source' and category 'Supporting'.

10. STARTUP ROADMAP (MANDATORY):
   - You MUST ALWAYS generate a dynamic, customized startup roadmap consisting of 5 to 7 sequential execution phases tailored to this specific startup idea.
   - Each phase must contain: step_number, phase_name, description, and estimated_timeline (e.g. 'Months 1-2').
   - NEVER return an empty roadmap list.

STRICT CONSTRAINTS:
- Do NOT include location maps or map coordinates.
- Do NOT invent facts or financial figures.
- Clearly mark unverified information as "Not verified".
"""

    result = structured_llm.invoke(prompt)

    return {
        "startup_intelligence": result.model_dump(),
    }