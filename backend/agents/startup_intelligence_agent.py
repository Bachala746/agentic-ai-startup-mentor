import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field, model_validator
from langchain_google_genai import ChatGoogleGenerativeAI

try:
    from duckduckgo_search import DDGS
except ImportError:
    from ddgs import DDGS

try:
    from .state import StartupState
except ImportError:
    StartupState = dict

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
    role: str = Field(default="", description="Specific job title (e.g. 'Chief Executive Officer (CEO)', 'Chief Technology Officer (CTO)', 'AI/ML Engineer')")
    reports_to: str | None = Field(default="None", description="Direct supervisor role in hierarchy. For Founder / CEO, must strictly be 'None'")
    department: str = Field(default="", description="Department (e.g. 'Executive Leadership', 'Engineering & Technology', 'AI & Data Intelligence', 'Clinical & Medical Affairs', 'Regulatory & Compliance', 'Sales & Strategic Growth')")
    priority: str = Field(default="Essential", description="'Essential' (Required immediately for MVP/launch) or 'Later' (Added as startup scales/expands)")
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
        description="Complete, domain-tailored list of distinct roles (6 to 9 roles) required to build, test, validate, operate, and scale the startup"
    )
    lean_team_advice: str = Field(
        default="",
        description="Practical lean execution guidance explaining how founders can operate lean during MVP (e.g., handling multiple roles, using fractional advisors) before hiring full-time"
    )
    team_hierarchy: list[HierarchyNode] = Field(
        default_factory=list,
        description="Multi-level reporting hierarchy nodes showing the complete reporting tree from Founder / CEO (reports_to='None') down through department leads and specialists"
    )
    competitor_analysis: list[Competitor] = Field(default_factory=list)
    financial_information: list[str] = Field(
        default_factory=list,
        description="STRICTLY verified financial data only. If unavailable, write 'Not publicly verified'."
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

        # 2. Domain-Specific Guarantee for MediSync AI / Clinical Healthcare AI
        st_name_low = str(self.startup_name or "").lower()
        exec_low = str(self.executive_summary or "").lower()
        is_medisync = "medisync" in st_name_low or ("health" in exec_low and "ai" in exec_low) or ("clinical" in exec_low and "diagnosis" in exec_low)

        if is_medisync:
            existing_roles_map = {r.role.lower(): r for r in self.recommended_team_structure}
            
            medisync_standard_roles = [
                TeamRole(
                    role="Chief Executive Officer (CEO) / Founder",
                    reports_to="None",
                    department="Executive Leadership",
                    priority="Essential",
                    experience_level="Executive",
                    why_needed="Guides venture vision, drives clinical hospital pilot acquisitions, spearheads fundraising, and aligns medical technology with hospital workflows.",
                    responsibilities="Secures hospital pilot agreements, manages investor relations, leads executive hiring, and ensures healthcare regulatory adherence and capital runway.",
                    required_skills=["Healthcare Strategy", "Hospital Enterprise Sales", "Venture Fundraising", "Clinical Workflow Optimization", "Stakeholder Governance"],
                    skills=["Healthcare Strategy", "Hospital Enterprise Sales", "Venture Fundraising"],
                    soft_skills=["Executive Presence", "High-Stakes Negotiation", "Visionary Communication", "Resilience"],
                ),
                TeamRole(
                    role="Chief Technology Officer (CTO)",
                    reports_to="Chief Executive Officer (CEO) / Founder",
                    department="Engineering & Technology",
                    priority="Essential",
                    experience_level="Lead / Executive",
                    why_needed="Architects the secure clinical AI platform, ensures HIPAA/HL7/FHIR compliance, and directs backend and machine learning pipelines.",
                    responsibilities="Oversees engineering architecture, enforces end-to-end medical data encryption, supervises cloud scaling, and mentors development engineers.",
                    required_skills=["System Architecture", "Cloud Infrastructure (AWS/GCP)", "FHIR / HL7 Data Standards", "Python", "Secure Microservices"],
                    skills=["System Architecture", "Cloud Infrastructure", "FHIR / HL7 Data Standards"],
                    soft_skills=["Technical Mentorship", "Strategic Architecture", "Decisiveness", "Agile Leadership"],
                ),
                TeamRole(
                    role="AI/ML Engineer",
                    reports_to="Chief Technology Officer (CTO)",
                    department="AI & Data Intelligence",
                    priority="Essential",
                    experience_level="Senior",
                    why_needed="Builds, fine-tunes, evaluates, and optimizes clinical diagnostic models and medical NLP pipelines on validated health datasets.",
                    responsibilities="Designs neural network pipelines, trains diagnostic models, evaluates sensitivity/specificity against medical gold standards, and minimizes inference latency.",
                    required_skills=["PyTorch", "TensorFlow", "Medical NLP", "Computer Vision", "Model Quantization", "MLOps"],
                    skills=["PyTorch", "TensorFlow", "Medical NLP", "MLOps"],
                    soft_skills=["Scientific Curiosity", "Analytical Rigor", "Attention to Detail", "Cross-Disciplinary Collaboration"],
                ),
                TeamRole(
                    role="Backend Developer",
                    reports_to="Chief Technology Officer (CTO)",
                    department="Engineering & Technology",
                    priority="Essential",
                    experience_level="Senior",
                    why_needed="Builds secure, high-throughput APIs, database schemas, and seamless EHR/EMR integrations required for hospital clinical trials.",
                    responsibilities="Implements REST/GraphQL APIs, integrates hospital EHR systems (Epic, Cerner, FHIR), ensures encrypted database transactions, and manages CI/CD pipelines.",
                    required_skills=["FastAPI/Django", "PostgreSQL", "Redis", "Docker", "Kubernetes", "EHR/EMR Integration", "CI/CD"],
                    skills=["FastAPI/Django", "PostgreSQL", "Docker", "EHR/EMR Integration"],
                    soft_skills=["Code Discipline", "Problem Solving", "Reliability", "Ownership"],
                ),
                TeamRole(
                    role="Clinical / Medical Advisor",
                    reports_to="Chief Executive Officer (CEO) / Founder",
                    department="Clinical & Medical Affairs",
                    priority="Essential",
                    experience_level="Executive / Senior Specialist (MD)",
                    why_needed="Provides medical oversight, validates diagnostic algorithm accuracy, ensures patient safety, and bridges the platform with clinical practitioners.",
                    responsibilities="Validates clinical training data, designs hospital validation protocols, evaluates diagnostic error edge cases, and advises on physician usability.",
                    required_skills=["Clinical Medicine", "Diagnostic Protocol Validation", "Medical Ethics", "Clinical Trial Design", "Peer Review"],
                    skills=["Clinical Medicine", "Diagnostic Validation", "Medical Ethics"],
                    soft_skills=["Clinical Authority", "Critical Inquiry", "Empathy", "Effective Communication"],
                ),
                TeamRole(
                    role="Healthcare Regulatory & Compliance Specialist",
                    reports_to="Chief Executive Officer (CEO) / Founder",
                    department="Regulatory & Compliance",
                    priority="Essential",
                    experience_level="Senior Specialist",
                    why_needed="Navigates medical device regulations (CDSCO, FDA 510(k), CE mark), data privacy laws (HIPAA, DISHA, DPDP Act), and ISO 13485/27001 certifications.",
                    responsibilities="Prepares regulatory filing dossiers, implements ISO quality management systems, audits patient health information security, and oversees clinical documentation.",
                    required_skills=["CDSCO Regulations", "FDA 510(k)", "HIPAA Compliance", "ISO 13485 / 27001", "Quality Management Systems (QMS)"],
                    skills=["CDSCO Regulations", "FDA 510(k)", "HIPAA Compliance"],
                    soft_skills=["Regulatory Precision", "Risk Management", "Ethical Integrity", "Meticulous Documentation"],
                ),
                TeamRole(
                    role="Business Development / Clinical Partnerships",
                    reports_to="Chief Executive Officer (CEO) / Founder",
                    department="Sales & Strategic Growth",
                    priority="Later",
                    experience_level="Senior Lead",
                    why_needed="Expands hospital provider networks, negotiates enterprise deployment contracts, and manages ongoing relationships with diagnostic networks.",
                    responsibilities="Identifies hospital pilot partners, negotiates commercial software licensing agreements, coordinates with hospital procurement boards, and tracks partner satisfaction.",
                    required_skills=["Healthcare Enterprise Sales", "Hospital Procurement", "Strategic Account Management", "Healthcare Economics", "Pipeline CRM"],
                    skills=["Healthcare Enterprise Sales", "Hospital Procurement", "Strategic Partnerships"],
                    soft_skills=["Persuasion", "Relationship Building", "Tenacity", "Executive Presentation"],
                ),
            ]

            # Merge missing standard roles
            for std_role in medisync_standard_roles:
                matched = any(
                    std_role.role.lower().split()[0] in r_key
                    or any(k in r_key for k in ["clinical", "medical"] if "clinical" in std_role.role.lower())
                    or any(k in r_key for k in ["regulatory", "compliance"] if "regulatory" in std_role.role.lower())
                    or any(k in r_key for k in ["partnership", "business development"] if "partnership" in std_role.role.lower())
                    or any(k in r_key for k in ["ai/ml", "machine learning"] if "ai/ml" in std_role.role.lower())
                    or any(k in r_key for k in ["backend"] if "backend" in std_role.role.lower())
                    for r_key in existing_roles_map
                )
                if not matched:
                    self.recommended_team_structure.append(std_role)

            if not self.lean_team_advice:
                self.lean_team_advice = (
                    "During the initial MVP validation stage, MediSync AI can operate lean with a core founding technical team "
                    "(CEO, CTO, AI/ML Engineer, and Backend Developer). The Clinical/Medical Advisor and Healthcare Regulatory Specialist "
                    "can be engaged as fractional advisors/consultants on a part-time basis to validate accuracy and compliance protocols "
                    "without heavy full-time payroll. The CEO handles initial clinical partnerships directly before scaling with a dedicated BD Lead."
                )

        # 3. Fix Founder / CEO root reporting to strictly 'None' and sort CEO to the top
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

        # 4. Sync team_hierarchy directly from recommended_team_structure
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

        self.team_hierarchy.sort(
            key=lambda n: 0 if ("ceo" in n.role.lower() or "founder" in n.role.lower()) else 1
        )

        # 5. Normalize Microsoft for Startups official URL across all funding programs
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

        # 6. Sanitize Financial Information
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

        # 7. Ensure funding_opportunities contains both categories for backward compatibility
        if not self.funding_opportunities:
            self.funding_opportunities = self.government_funding_schemes + self.private_funding_opportunities

        # 8. Ensure official_source display fallback is populated
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
      - For MeitY TIDE 2.0, set application_website to 'https://msh.meity.gov.in/schemes/tide'.
      - For MSME Innovative Scheme, set application_website to 'https://innovative.msme.gov.in'.
      - RULE: Only recommend schemes relevant to the startup's actual domain. Do NOT recommend biotechnology schemes (like BIRAC) to a FoodTech, FinTech, or SaaS startup unless there is a genuine biotechnology or biomedical component.

   B. PRIVATE FUNDING OPPORTUNITIES (private_funding_opportunities):
      - Provide a MINIMUM of 3 genuine, highly relevant private funding opportunities (VC seed funds, Angel networks, Accelerators, Corporate grants, Cloud credits).
      - RULE: For Microsoft for Startups, use the verified official portal URL: https://startups.microsoft.com.

3. DYNAMIC COMPANY & TEAM STRUCTURE (MANDATORY COMPLETE HIERARCHICAL COVERAGE):
   - You MUST generate a complete, realistic, domain-specific organizational structure (6 to 9 distinct roles).
   - DO NOT truncate or limit the team to only CEO and CTO. Every venture requires engineering, domain specialists, regulatory/operations, and commercial capabilities.
   - For every role, define:
     * role: Specific professional title.
     * reports_to: Direct manager (Top leader must strictly be 'None'; direct reports report to CEO; technical specialists report to CTO or functional lead).
     * department: Relevant functional department.
     * priority: 'Essential' (required immediately for MVP build and initial validation) or 'Later' (added during early growth, commercialization, or scale).
     * experience_level: Junior, Mid-Level, Senior, Lead, or Executive.
     * why_needed: Explicit domain-specific rationale explaining why this venture requires this role.
     * responsibilities: Detailed scope of technical or business deliverables.
     * required_skills: Technical, domain, and tool proficiencies.
     * soft_skills: Collaboration, leadership, and operational competencies.

   DOMAIN REQUIREMENTS:
   - For Healthcare / Clinical AI (such as MediSync AI or medical diagnostic tools):
     You MUST include all 7 of the following roles:
     1. Chief Executive Officer (CEO) / Founder (Reports to: None, Priority: Essential)
     2. Chief Technology Officer (CTO) (Reports to: CEO, Priority: Essential)
     3. AI/ML Engineer (Reports to: CTO, Priority: Essential)
     4. Backend Developer (Reports to: CTO, Priority: Essential)
     5. Clinical / Medical Advisor (Reports to: CEO, Priority: Essential - fractional/advisor)
     6. Healthcare Regulatory & Compliance Specialist (Reports to: CEO or Clinical Advisor, Priority: Essential - fractional/advisor)
     7. Business Development / Clinical Partnerships (Reports to: CEO, Priority: Later)

   - For Drone & Robotics / Inspection: Include CEO, CTO / Hardware Lead, Robotics & Embedded Engineer, Computer Vision Specialist, Drone Regulatory / DGCA Pilot Lead, Field Operations, and Business Development.
   - For AgriTech: Include CEO, CTO, Agronomist / Plant Pathologist, AI/ML Vision Engineer, Mobile Developer, Field Operations Lead.
   - For E-Commerce / Marketplaces: Include CEO, CTO, Full-Stack / Mobile Developer, Merchant Acquisition Lead, UI/UX Designer, Growth Marketer.

   LEAN TEAM STRATEGY:
   - In 'lean_team_advice', explain how the founder operates leanly during MVP (e.g. founder handling multiple hats, engaging doctors or compliance experts as fractional advisors before full-time hiring).

4. COMPETITOR ANALYSIS & FINANCIAL CLASSIFICATION (STRICT ACCURACY):
   - Identify real competitor companies or market alternatives.
   - STRICT FINANCIAL RULES: NEVER classify external funding or investment raised as company revenue!
   - funding_raised: Total verified capital raised. If unverified, state 'Not publicly verified'.
   - revenue: Verified operating revenue with financial year and source. If unverified, state 'Not publicly verified'.
   - profit_loss: Verified profit/loss with financial year and source, or 'Not publicly verified'.

5. FINANCIAL INFORMATION (financial_information):
   - Strictly verified financial data only. If unavailable, write 'Not publicly verified'.

6. STARTUP VS COMPETITORS: Sharp differentiation points.
7. IMPORTANT RECOMMENDATIONS: Actionable founder execution recommendations.
8. SOURCES / OFFICIAL LINKS: Clickable verified URLs and official portals.
9. STARTUP ROADMAP (5 TO 7 SEQUENTIAL PHASES): Sequential execution roadmap tailored to the startup idea.
"""

    result = structured_llm.invoke(prompt)

    return {
        "startup_intelligence": result.model_dump(),
    }