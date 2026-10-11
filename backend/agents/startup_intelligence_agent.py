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
    name: str = Field(default="", description="Exact name of ONE specific funding program or scheme (NEVER combine two programs like 'BIRAC / MeitY')")
    organization: str = Field(default="", description="Official ministry, government body, corporation, VC, or accelerator providing the program")
    funding_type: str = Field(
        default="Grant",
        description="Type: Grant, Equity Investment, Debt, Accelerator Funding, Corporate Program, Cloud Credits, Incubator, Credit/Support, Other"
    )
    funding_amount: str = Field(default="Not verified", description="Verified monetary funding amount, grant value, or credits (e.g. 'Up to ₹50 Lakhs', '$100,000 in cloud credits'). Never invent amounts.")
    eligibility: str = Field(default="Not verified", description="Key verified eligibility criteria (incorporation age, sector, DPIIT recognition, etc.)")
    who_can_apply: str = Field(default="Not verified", description="Eligible legal entities (e.g. Private Limited, LLP, student entrepreneurs, registered entities)")
    startup_stage: str = Field(default="Not verified", description="Stage: Ideation, Validation, Prototype/MVP, Early Traction, Scaling")
    usage: str = Field(default="Not verified", description="Permitted use of funds or credit resources (e.g. Proof of Concept, prototyping, cloud compute, market entry)")
    where_to_apply: str = Field(default="Not verified", description="Official portal, implementing agency, or participating incubator")
    application_website: str = Field(
        default="Not verified",
        description="Direct official portal URL for applications. If unverified, state 'Not verified'"
    )
    application_steps: list[str] = Field(default_factory=list, description="Step-by-step application instructions")
    required_documents: list[str] = Field(default_factory=list, description="List of officially required documents (pitch deck, KYC, DPIIT cert, etc.)")
    deadline: str = Field(default="Not verified", description="Verified application deadline or 'Ongoing' / 'Cohort-based' / 'Not verified'")
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
    why_suitable: str = Field(default="", description="Why this opportunity aligns directly with this specific startup idea, domain, and stage")


class TeamRole(BaseModel):
    role: str = Field(default="", description="Specific job title (e.g. 'Chief Executive Officer (CEO)', 'CTO', 'Backend Lead')")
    reports_to: str | None = Field(default="None", description="Direct supervisor role in hierarchy. For Founder / CEO, must strictly be 'None'")
    department: str = Field(default="", description="Department (e.g. 'Executive Leadership', 'Engineering', 'AI/ML', 'Product', 'Operations', 'Clinical & Compliance', 'Sales & Growth')")
    priority: str = Field(default="Essential", description="'Essential' (Immediately required for MVP/launch) or 'Later' (Needed when startup scales/expands)")
    experience_level: str = Field(default="Mid-Level", description="Experience tier: Junior, Mid-Level, Senior, Lead, or Executive")
    responsibilities: str = Field(default="", description="Core duties, operational ownership, architecture deliverables, and scope")
    required_skills: list[str] = Field(default_factory=list, description="Core technical, domain-specific, and tool proficiencies")
    skills: list[str] = Field(default_factory=list, description="Backward-compatible alias for required skills")
    soft_skills: list[str] = Field(default_factory=list, description="Essential communication, ownership, and collaborative competencies")
    why_needed: str = Field(default="", description="Startup-specific justification explaining why this role is needed for this exact domain, product architecture, and stage")


class HierarchyNode(BaseModel):
    role: str = Field(default="", description="Role title in the hierarchy tree")
    reports_to: str | None = Field(default="None", description="Direct supervisor role ('None' for the root Founder / CEO)")
    department: str = Field(default="", description="Department or functional area")
    priority: str = Field(default="Essential", description="'Essential' or 'Later'")


class Competitor(BaseModel):
    name: str = Field(default="", description="Real competitor company or product name")
    product_service: str = Field(default="", description="Core product or service offering")
    target_customers: str = Field(default="", description="Target customer segments and markets")
    business_model: str = Field(default="", description="Monetization and business model")
    pricing: str = Field(default="Not publicly verified", description="Verified pricing tiers or structure")
    strengths: list[str] = Field(default_factory=list, description="Key competitor advantages and moat")
    weaknesses: list[str] = Field(default_factory=list, description="Identified competitor market gaps, complaints, or weaknesses")
    funding_raised: str = Field(
        default="Not publicly verified",
        description="Total verified external funding/investment raised (e.g. '$16M across Series A'). Do NOT classify as revenue!"
    )
    revenue: str = Field(
        default="Not publicly verified",
        description="Verified revenue with financial year and source (e.g. '₹45 Cr (FY 2024) - MCA Filing'). NEVER classify investment/funding raised as revenue!"
    )
    profit_loss: str = Field(
        default="Not publicly verified",
        description="Verified profit/loss with financial year and source, or 'Not publicly verified'"
    )
    source: str = Field(default="", description="Source for financial/company data (e.g. MCA filing, Tracxn, Crunchbase, Annual Report)")


class SourceItem(BaseModel):
    name: str = Field(default="", description="Descriptive name of the source (e.g. 'BIRAC Official Portal', 'Startup India Seed Fund')")
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
    startup_name: str = Field(default="", description="Identified or proposed name for the startup idea")
    executive_summary: str = Field(default="", description="Executive summary of intelligence findings")
    government_funding_schemes: list[FundingOpportunity] = Field(
        default_factory=list,
        description="Government grants, startup schemes, seed funds, institutional loans, and official incubator programs (MINIMUM 3 distinct schemes)"
    )
    private_funding_opportunities: list[FundingOpportunity] = Field(
        default_factory=list,
        description="Private programs, VC funding, corporate grants, angel networks, accelerators, and corporate credits (MINIMUM 3 distinct opportunities)"
    )
    funding_opportunities: list[FundingOpportunity] = Field(
        default_factory=list,
        description="Consolidated list of all funding opportunities for backward compatibility"
    )
    recommended_team_structure: list[TeamRole] = Field(
        default_factory=list,
        description="Dynamic, domain-tailored list of distinct roles required to build, test, operate, and scale the startup"
    )
    team_hierarchy: list[HierarchyNode] = Field(
        default_factory=list,
        description="Multi-level reporting hierarchy nodes showing the complete reporting tree from Founder / CEO (reports_to='None') down through department heads, leads, and specialists"
    )
    competitor_analysis: list[Competitor] = Field(default_factory=list)
    financial_information: list[str] = Field(
        default_factory=list,
        description="STRICTLY verified financial data only (Revenue, Profit/Loss, Funding Raised, Financial Year, Source). If unavailable, write 'Not publicly verified'. Absolutely NO industry benchmarks, estimated percentages, capital allocations, or advice."
    )
    startup_vs_competitors: list[str] = Field(default_factory=list)
    important_recommendations: list[str] = Field(default_factory=list)
    sources: list[SourceItem] = Field(default_factory=list)
    roadmap: list[RoadmapStep] = Field(
        default_factory=list,
        description="Sequential 5 to 7 phase execution roadmap tailored to the startup idea"
    )

    @model_validator(mode="after")
    def sync_and_validate_report(self):
        # 1. Sync skills and required_skills for TeamRole
        for role in self.recommended_team_structure:
            if not role.skills and role.required_skills:
                role.skills = role.required_skills
            elif not role.required_skills and role.skills:
                role.required_skills = role.skills

        # 2. Fix Founder / CEO root reporting to strictly 'None' and sort CEO to the top
        for role in self.recommended_team_structure:
            r_lower = role.role.strip().lower()
            if "ceo" in r_lower or "founder" in r_lower:
                role.reports_to = "None"
            elif role.reports_to:
                rep_lower = str(role.reports_to).strip().lower()
                if rep_lower in [r_lower, "", "none", "null"]:
                    role.reports_to = "None"

        # Ensure CEO/Founder is first in recommended_team_structure
        self.recommended_team_structure.sort(
            key=lambda r: 0 if ("ceo" in r.role.lower() or "founder" in r.role.lower()) else 1
        )

        # 3. Sync team_hierarchy from recommended_team_structure if missing or incomplete
        if (not self.team_hierarchy or len(self.team_hierarchy) < len(self.recommended_team_structure)) and self.recommended_team_structure:
            self.team_hierarchy = [
                HierarchyNode(
                    role=r.role,
                    reports_to=r.reports_to,
                    department=r.department,
                    priority=r.priority,
                )
                for r in self.recommended_team_structure
            ]

        for node in self.team_hierarchy:
            r_lower = node.role.strip().lower()
            if "ceo" in r_lower or "founder" in r_lower:
                node.reports_to = "None"
            elif node.reports_to:
                rep_lower = str(node.reports_to).strip().lower()
                if rep_lower in [r_lower, "", "none", "null"]:
                    node.reports_to = "None"

        # Ensure CEO is first in team_hierarchy
        self.team_hierarchy.sort(
            key=lambda n: 0 if ("ceo" in n.role.lower() or "founder" in n.role.lower()) else 1
        )

        # 4. Normalize Microsoft for Startups official URL across all funding programs
        all_opps = self.government_funding_schemes + self.private_funding_opportunities + self.funding_opportunities
        for opp in all_opps:
            opp_text = f"{opp.name} {opp.organization} {opp.official_source_name}".lower()
            if "microsoft for startups" in opp_text or "founders hub" in opp_text:
                if not opp.application_website or opp.application_website == "Not verified" or "startup.microsoft.com" in opp.application_website.lower():
                    opp.application_website = "https://startups.microsoft.com"
                if not opp.official_source_url or opp.official_source_url == "Not verified" or "startup.microsoft.com" in opp.official_source_url.lower():
                    opp.official_source_url = "https://startups.microsoft.com"

        # Normalize Microsoft for Startups in sources
        for src in self.sources:
            if "microsoft for startups" in src.name.lower() or "founders hub" in src.name.lower():
                if not src.url or "startup.microsoft.com" in src.url.lower():
                    src.url = "https://startups.microsoft.com"

        # 5. Sanitize Financial Information (Reject "Internal Startup Assessment")
        cleaned_financials = []
        for fin in self.financial_information:
            if "internal startup assessment" in str(fin).lower() or "internal assessment" in str(fin).lower():
                cleaned_financials.append("Not publicly verified")
            else:
                cleaned_financials.append(fin)
        self.financial_information = cleaned_financials or ["Not publicly verified"]

        for comp in self.competitor_analysis:
            if "internal startup assessment" in str(comp.source).lower() or "internal assessment" in str(comp.source).lower():
                comp.source = "Public market intelligence"
            if "internal startup assessment" in str(comp.revenue).lower():
                comp.revenue = "Not publicly verified"
            if "internal startup assessment" in str(comp.profit_loss).lower():
                comp.profit_loss = "Not publicly verified"
            if "internal startup assessment" in str(comp.funding_raised).lower():
                comp.funding_raised = "Not publicly verified"

        # 6. Ensure funding_opportunities contains both categories for backward compatibility
        if not self.funding_opportunities:
            self.funding_opportunities = self.government_funding_schemes + self.private_funding_opportunities

        # 7. Ensure official_source display fallback is populated
        for opp in all_opps:
            if not opp.official_source or opp.official_source == "Not verified":
                if opp.official_source_name and opp.official_source_name != "Not verified":
                    opp.official_source = opp.official_source_name
                elif opp.organization and opp.organization != "Not verified":
                    opp.official_source = opp.organization

        return self


# ============================================================================
# LLM SETUP
# ============================================================================

model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

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
        f"{startup_idea} startup team structure tech stack domain requirements",
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

    return unique[:30]


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
You are the Startup Intelligence Agent, an expert startup advisor and tech intelligence strategist.

Analyze the given startup idea in depth using the founder profile and the CURRENT web research findings.

STARTUP IDEA:
{startup_idea}

FOUNDER PROFILE:
{founder_profile}

CURRENT WEB RESEARCH:
{web_information}

Generate a comprehensive, strictly accurate Startup Intelligence Report adhering to the following rules:

1. EXECUTIVE SUMMARY & STARTUP OVERVIEW:
   - Propose an appropriate startup name for the venture (set startup_name).
   - Provide an incisive executive summary of the target market, funding landscape, competitive dynamics, and pragmatic operational strategy tailored to the founder's background.

2. FUNDING OPPORTUNITIES (MINIMUM 3 GOVERNMENT & MINIMUM 3 PRIVATE — STRICTLY SEPARATED):
   A. GOVERNMENT FUNDING SCHEMES (government_funding_schemes):
      - Provide a MINIMUM of 3 genuine, highly relevant government funding schemes, grants, or seed funds (e.g. SISFS, BIRAC BIG, NIDHI-PRAYAS, MeitY TIDE 2.0, MSME Innovative Scheme, PMEGP, CGTMSE, DBT, DST, State Startup Seed Funds) specifically applicable to the startup's domain and stage.
      - RULE: NEVER combine two unrelated programs into one entry (e.g. DO NOT write 'BIRAC BIG / MeitY TIDE 2.0'). Each scheme must be a separate, individual entry.
      - RULE: Only recommend schemes relevant to the startup's actual domain. Do NOT recommend biotechnology schemes (like BIRAC) to a FoodTech, FinTech, or SaaS startup unless there is a genuine biotechnology or biomedical component.
      - For each scheme, provide all required fields: name, organization, funding_type, funding_amount, eligibility, who_can_apply, startup_stage, usage, where_to_apply, application_website, application_steps, required_documents, deadline, official_source_name, official_source_url, and why_suitable.

   B. PRIVATE FUNDING OPPORTUNITIES (private_funding_opportunities):
      - Provide a MINIMUM of 3 genuine, highly relevant private funding opportunities (e.g. VC seed funds, Angel networks like Indian Angel Network / Mumbai Angels, Accelerators like Techstars / Y Combinator / Surge / Axilor, Corporate startup programs, Corporate grants, Cloud credits like AWS Activate / Google for Startups / Microsoft for Startups).
      - RULE: Do NOT treat cloud credits as cash funding. Explicitly categorize funding_type: Grant, Equity Investment, Debt, Accelerator Funding, Corporate Program, Cloud Credits, Incubator, Credit/Support, or Other.
      - RULE: For Microsoft for Startups, use the verified official portal URL: https://startups.microsoft.com.
      - For each opportunity, provide all required fields listed above.

   C. ANTI-HALLUCINATION & SOURCE VERIFICATION:
      - official_source_name: Must be the ACTUAL government ministry/body or the company/VC running the program.
      - official_source_url & application_website: Must be the actual verified official portal URL. If unverified, state 'Not verified'.
      - ABSOLUTE RULE: NEVER cite a third-party blog or aggregator as an 'Official Source'.
      - NEVER invent funding amounts, eligibility rules, deadlines, or URLs. If a deadline is ongoing or unspecified, state 'Not verified'.

    3. DYNAMIC COMPANY & TEAM STRUCTURE:

       MAIN OBJECTIVE:
       Generate a realistic team structure specifically for the given startup idea.
       The hierarchy must change according to the startup's actual domain,
       technology, business model, and operational requirements.

       A. DYNAMIC ROLE SELECTION:
       - Identify the startup's domain before selecting roles.
       - Select only roles relevant to building and operating this startup.
       - Consider technical, product, domain-specialist, operational,
         compliance, marketing, and business functions where appropriate.
       - Do not force the same departments or roles into every startup.
       - Do not add unnecessary roles merely to make the hierarchy larger.
       - Include domain-specific specialists when the startup genuinely needs them.
       - Explain why each role is needed for this particular startup.

       B. TEAM HIERARCHY:
       The hierarchy must answer:
       - Who leads the company?
       - Which departments are required?
       - Who reports to whom?
       - Which roles are essential for the MVP?
       - Which roles can be added later?

       Use a logical multi-level reporting structure:
       Level 1: CEO / Founder.
       Level 2: Relevant department heads or direct reports to the CEO.
       Level 3: Team leads reporting to their department heads.
       Level 4: Developers, engineers, specialists, testers, and executives
                reporting to their appropriate leads.

       This is a flexible guide, NOT a fixed hierarchy.
       Create only the levels and roles appropriate to the startup.
       Small startups may have fewer levels.

       C. REPORTING RULES:
       - CEO / Founder must have reports_to = "None".
       - Never make the CEO report to themselves or another role.
       - Direct reports of the CEO must have reports_to set to
         "Chief Executive Officer (CEO)" when that is the generated CEO title.
       - Every other role must report to its actual direct manager.
       - Every reports_to value must match an existing role title exactly,
         except the CEO's value, which must be "None".
       - Avoid circular reporting relationships.
       - Include a corresponding team_hierarchy node for every role
         in recommended_team_structure.
       - Keep the hierarchy connected to the CEO.

       D. ESSENTIAL AND LATER ROLES:
       For every role, set priority to one of:
       - "Essential": Needed to build, validate, launch, or operate the MVP.
       - "Later": Can be introduced when the startup expands or scales.
       Decide priority based on the actual startup idea and its stage.

       E. ROLE DETAILS:
       For every recommended_team_structure role, provide:
       - role: Specific job title.
       - reports_to: Direct manager's exact role title, or "None" for CEO.
       - department: Relevant functional department.
       - priority: "Essential" or "Later".
       - experience_level: Junior, Mid-Level, Senior, Lead, or Executive.
       - responsibilities: Specific duties and deliverables.
       - required_skills: Relevant technical and domain-specific skills.
       - soft_skills: Relevant collaboration and communication skills.
       - why_needed: Why the role is necessary for this startup.

       F. TEAM HIERARCHY OUTPUT:
       For every role, create a corresponding team_hierarchy node containing:
       - role
       - reports_to
       - department
       - priority

       The hierarchy must accurately represent the reporting relationships
       defined in recommended_team_structure.

       G. STRICT RESTRICTIONS:
       - Do not use a fixed hierarchy for every startup.
       - Do not add irrelevant roles from unrelated domains.
       - Do not include employee counts, headcounts, or employee multipliers.
       - Do not put employee counts inside hierarchy nodes.
       - Do not repeat roles unnecessarily.
       - Keep the structure readable and suitable for a startup founder.

        H. COMPLETE, DOMAIN-SPECIFIC TEAM COVERAGE:

       Generate a complete team structure based on the actual startup idea,
       domain, product, technology, customers, and business model.

       1. CONSIDER ALL RELEVANT FUNCTIONS:
       - Leadership: CEO / Founder, CTO.
       - Backend: Backend Developer, API Developer.
       - Frontend: Frontend Developer, Full Stack Developer.
       - AI and Data: AI/ML Engineer, Data Engineer, Data Scientist.
       - Design: UI/UX Designer, Product Designer.
       - Quality: QA Engineer, Test Engineer.
       - Infrastructure: DevOps Engineer, Cloud Engineer.
       - Security: Cybersecurity Specialist.
       - Product: Product Manager, Business Analyst.
       - Business: Sales Manager, Marketing Manager,
         Business Development Manager, Partnerships Manager.
       - Operations: Operations Manager, Customer Support Specialist.
       - Domain experts: Select specialists relevant to the startup idea.

       These are candidate roles, not a mandatory fixed list.

       2. ROLE SELECTION:
       - Evaluate every function above against the actual startup idea.
       - Include all functions genuinely needed to build, launch, sell,
         support, and operate the product.
       - Do not omit frontend, UI/UX, QA, DevOps, sales, or marketing
         merely because the startup is technology-focused.
       - Include domain-specific experts when the product requires them.
       - Avoid irrelevant or duplicate roles.
       - For a small startup, one person may perform multiple functions.
         Represent separate roles only when they are genuinely needed.

       3. DOMAIN-SPECIFIC REQUIREMENTS:
       - Healthcare: Consider radiologists, clinical advisors,
         medical data specialists, and regulatory experts.
       - Agriculture: Consider agricultural specialists,
         field operations, IoT, and crop experts where relevant.
       - Drones/Robotics: Consider robotics, embedded systems,
         electronics, and computer vision specialists.
       - Education: Consider educators, curriculum designers,
         learning-experience designers, and student support.
       - FinTech: Consider financial experts, risk analysts,
         cybersecurity, and compliance specialists.
       - For other domains, identify the appropriate specialists
         from the actual product requirements.

       4. PRIORITY:
       Every role must have priority:
       - "Essential": Needed for the MVP or its initial operation.
       - "Later": Useful for growth, expansion, or scaling.
       Base this decision on the actual startup idea and stage.

       5. REPORTING STRUCTURE:
       - CEO / Founder must be the top-level role and have reports_to = "None".
       - Assign each other role to its actual direct manager.
       - Every manager referenced by reports_to must exist in the role list.
       - Avoid circular reporting relationships.
       - Keep the hierarchy connected to the CEO.
       - Include every selected role in both recommended_team_structure
         and team_hierarchy.
       - Keep role titles and reporting relationships consistent
         across both structures.

       6. REQUIRED ROLE INFORMATION:
       For every role provide:
       - role
       - reports_to
       - department
       - priority
       - experience_level
       - responsibilities
       - required_skills
       - soft_skills
       - why_needed

       7. HIERARCHY RULES:
       - Generate a hierarchy specific to each startup idea.
       - Do not force the same departments onto every startup.
       - Do not omit necessary business or product functions.
       - Do not include employee counts or headcounts in hierarchy nodes.
       - Do not invent unnecessary roles just to make the team larger.
       - Ensure the final hierarchy matches the recommended role list.

4. COMPETITOR ANALYSIS & FINANCIAL CLASSIFICATION (STRICT ACCURACY):
   - Identify real competitor companies or market alternatives.
   - STRICT FINANCIAL RULES:
     * NEVER classify external funding or investment raised as company revenue!
     * funding_raised: Total verified external capital raised (e.g. '$16M across Series A'). If unverified, state 'Not publicly verified'.
     * revenue: Verified operating revenue with financial year and source (e.g. '₹45 Cr (FY 2024) - MCA Filing'). If unverified, state 'Not publicly verified'.
     * profit_loss: Verified profit/loss with financial year and source, or 'Not publicly verified'.
     * If no verified operating revenue exists in public records, explicitly write 'Not publicly verified'. NEVER fabricate numbers.

5. FINANCIAL INFORMATION (financial_information):
   STRICT FINANCIAL INFORMATION RULE:
   - Only provide verified financial information from reliable sources.
   - Include Revenue, Profit/Loss, Funding Raised, Financial Year, and Source.
   - Format: "Revenue: [Value] | Profit/Loss: [Value] | Funding Raised: [Value] | Financial Year: [Year] | Source: [Source]"
   - If verified data is unavailable, write strictly: "Not publicly verified".
   - NEVER output 'Source: Internal Startup Assessment' or 'Internal Assessment'.
   - NEVER invent, estimate, approximate, or assume financial figures.
   - Do NOT put industry benchmarks (e.g. typical margins), market estimates, capital allocation percentages, target metrics (e.g. NRR, CAC/LTV), or general financial advice inside the Financial Information section.

6. STARTUP VS COMPETITORS:
   - Provide sharp comparison points highlighting advantages and differentiators.

7. IMPORTANT RECOMMENDATIONS:
   - Actionable, prioritized recommendations for the founder across technical MVP architecture, pilot validation, and funding strategy.

8. SOURCES / OFFICIAL LINKS (sources):
   - Provide verified sources used. Each source must have:
     * name: Descriptive name (e.g. 'Startup India Official Portal', 'Ministry of MSME')
     * url: Clickable verified URL (e.g. 'https://startups.microsoft.com' for Microsoft for Startups)
     * source_type: 'Official Government/Organization Source', 'Company Source', 'Financial Source', or 'Supporting / Reference Source'
     * category: 'Official' or 'Supporting'

9. STARTUP ROADMAP (5 TO 7 SEQUENTIAL PHASES):
   - Customized, sequential 5 to 7 phase execution roadmap tailored to the startup idea.
   - Each phase must contain: step_number, phase_name, description, and estimated_timeline.

STRICT CONSTRAINTS:
- Founder / CEO must strictly have reports_to = "None".
- Financial Information MUST ONLY contain verified financial metrics or "Not publicly verified". NO industry benchmarks, NO advice, NO internal assessments, and NO estimates.
- Do NOT output employee counts, headcount numbers, or employee multipliers anywhere.
- Do NOT include location maps or map coordinates.
- Do NOT fabricate financial numbers or URLs.
- Always provide at least 3 distinct government schemes and at least 3 distinct private funding opportunities.
"""

    result = structured_llm.invoke(prompt)

    return {
        "startup_intelligence": result.model_dump(),
    }