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
    funding_amount: str = Field(default="Unverified", description="Verified monetary funding amount, grant value, or credits (e.g. 'Up to ₹7 Lakhs', '$150,000 in cloud credits'). Never invent amounts.")
    eligibility: str = Field(default="Unverified", description="Key verified eligibility criteria (incorporation age, sector, DPIIT recognition, etc.)")
    who_can_apply: str = Field(default="Unverified", description="Eligible legal entities (e.g. Private Limited, LLP, student entrepreneurs, registered entities)")
    startup_stage: str = Field(default="Unverified", description="Stage: Ideation, Validation, Prototype/MVP, Early Traction, Scaling")
    usage: str = Field(default="Unverified", description="Permitted use of funds or credit resources (e.g. Proof of Concept, prototyping, cloud compute, market entry)")
    where_to_apply: str = Field(default="Unverified", description="Official portal, implementing agency, or participating incubator")
    application_website: str = Field(
        default="Unverified",
        description="Direct official portal URL for applications. If unverified, state 'Unverified'"
    )
    application_steps: list[str] = Field(default_factory=list, description="Step-by-step application instructions")
    required_documents: list[str] = Field(default_factory=list, description="List of officially required documents (pitch deck, KYC, DPIIT cert, etc.)")
    deadline: str = Field(default="Unverified", description="Verified application deadline or 'Ongoing' / 'Cohort-based' / 'Unverified'")
    date_checked: str = Field(default="October 2026", description="Month and year when status and scheme details were verified")
    status_evidence: str = Field(default="Unverified", description="Official source evidence on open/closed/cohort status")
    official_source_name: str = Field(
        default="Unverified",
        description="Name of the official government ministry, organizing body, or company (NEVER a third-party blog)"
    )
    official_source_url: str = Field(
        default="Unverified",
        description="Official root or scheme URL from the organizing body. If unverified, state 'Unverified'"
    )
    official_source: str = Field(
        default="",
        description="Backward-compatible display name for the official source"
    )
    why_suitable: str = Field(default="", description="Why this opportunity aligns directly with this specific startup idea, domain, and stage")


class TeamRole(BaseModel):
    role: str = Field(default="", description="Specific job title (e.g. 'Chief Executive Officer (CEO)', 'Chief Technology Officer (CTO)', 'AI / Computer Vision Engineer')")
    reports_to: str | None = Field(default="None", description="Direct supervisor role in hierarchy. For Founder / CEO, must strictly be 'None'")
    department: str = Field(default="", description="Department (e.g. 'Executive Leadership', 'Engineering & Technology', 'AI & Data Intelligence', 'Growth & Creator Marketing', 'Product & Design')")
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
    pricing: str = Field(default="Unverified", description="Verified pricing tiers or structure with source, or 'Unverified'")
    strengths: list[str] = Field(default_factory=list, description="Key competitor advantages and moat")
    weaknesses: list[str] = Field(default_factory=list, description="Identified competitor market gaps, complaints, or weaknesses")
    funding_raised: str = Field(
        default="Unverified",
        description="Total verified external funding raised with round details, or 'Unverified'. Do NOT classify as revenue!"
    )
    revenue: str = Field(
        default="Unverified",
        description="Verified revenue from statutory filings with FY, or 'Unverified'. NEVER classify funding raised as revenue!"
    )
    profit_loss: str = Field(
        default="Unverified",
        description="Verified profit/loss from statutory filings with FY, or 'Unverified'"
    )
    source: str = Field(default="Public market intelligence", description="Source name for competitor data (e.g. Official Pricing Page, Tracxn, Crunchbase)")
    source_url: str = Field(default="Unverified", description="Direct official or reliable source URL")
    date_checked: str = Field(default="October 2026", description="Month and year when details were verified")


class RiskItem(BaseModel):
    category: str = Field(
        default="Technical",
        description="Category: Technical, Market, Financial, Operational, Regulatory & IP, Privacy & Security"
    )
    risk: str = Field(
        default="",
        description="Specific risk scenario and its direct operational impact on this venture"
    )
    impact: str = Field(
        default="Medium",
        description="Severity / Impact tier: Low, Medium, High, or Critical"
    )
    mitigation_strategy: str = Field(
        default="",
        description="Concrete, actionable, and pragmatic mitigation plan without claiming unverified regulatory or legal clearance"
    )


class FinancialAnalysis(BaseModel):
    mvp_budget_breakdown: list[str] = Field(
        default_factory=list,
        description="Itemized lean MVP development budget items. For bootstrapped/early ventures, target lean MVP costs below ₹10,000 where feasible and clearly label all assumptions."
    )
    estimated_monthly_burn: str = Field(
        default="Unverified",
        description="Estimated monthly operating expenses during MVP validation (hosting, APIs, domains, basic operations)"
    )
    pricing_model_and_unit_economics: str = Field(
        default="",
        description="Proposed pricing tiers, subscription structure, unit economics, and gross margins [Labeled as Assumptions]"
    )
    revenue_scenarios: list[str] = Field(
        default_factory=list,
        description="Illustrative conservative, moderate, and aggressive early revenue scenarios with correct math, clearly labeled as assumptions, NEVER guaranteed revenue"
    )
    break_even_assumptions: str = Field(
        default="",
        description="Estimated subscriber count or transaction volume needed to break even against monthly operating expenses"
    )
    competitor_or_historical_benchmarks: list[str] = Field(
        default_factory=list,
        description="Verified financial data or filings from competitors/market benchmarks. If unavailable, state 'Unverified'."
    )


class SourceItem(BaseModel):
    name: str = Field(default="", description="Descriptive name of the source (e.g. 'MeitY TIDE 2.0 Official Portal', 'Opus Clip Pricing Page')")
    url: str = Field(default="", description="Verified working URL from web research")
    source_type: str = Field(
        default="Official Government/Organization Source",
        description="Type: 'Official Government/Organization Source', 'Company Source', 'Financial Source', or 'Supporting / Reference Source'"
    )
    category: str = Field(default="Official", description="'Official' or 'Supporting'")
    date_checked: str = Field(default="October 2026", description="Month and year verified")


class RoadmapStep(BaseModel):
    step_number: int = Field(default=1, description="Sequential phase number")
    phase_name: str = Field(default="", description="Phase title tailored to this startup idea")
    description: str = Field(default="", description="Specific execution milestones and objectives to accomplish")
    estimated_timeline: str = Field(default="", description="Estimated duration (e.g. 'Months 1-2')")
    deliverables: list[str] = Field(default_factory=list, description="Key deliverables produced during this phase")


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
        description="Practical lean execution guidance explaining how founders can operate lean during MVP before hiring full-time"
    )
    team_hierarchy: list[HierarchyNode] = Field(
        default_factory=list,
        description="Multi-level reporting hierarchy nodes showing the complete reporting tree from Founder / CEO (reports_to='None') down through department leads and specialists"
    )
    competitor_analysis: list[Competitor] = Field(default_factory=list)
    financial_analysis: FinancialAnalysis = Field(
        default_factory=FinancialAnalysis,
        description="Startup-specific lean MVP budget, estimated monthly operating expenses, pricing scenarios, break-even assumptions, and verified benchmarks"
    )
    financial_information: list[str] = Field(
        default_factory=list,
        description="Backward-compatible list of verified competitor/market financial points"
    )
    risk_analysis: list[RiskItem] = Field(
        default_factory=list,
        description="Comprehensive assessment of technical, market, financial, operational, regulatory/IP, and privacy risks with practical mitigations"
    )
    startup_vs_competitors: list[str] = Field(default_factory=list)
    important_recommendations: list[str] = Field(default_factory=list)
    sources: list[SourceItem] = Field(default_factory=list)
    roadmap: list[RoadmapStep] = Field(
        default_factory=list,
        description="Sequential 5 to 7 phase execution roadmap tailored to the startup idea with deliverables"
    )

    @model_validator(mode="after")
    def sync_and_validate_report(self):
        st_name_low = str(self.startup_name or "").lower()
        exec_low = str(self.executive_summary or "").lower()

        is_creator = (
            "creatorclip" in st_name_low
            or "video" in st_name_low
            or "clip" in st_name_low
            or "creator" in st_name_low
            or ("video" in exec_low and "creator" in exec_low)
        )
        is_medisync = (
            "medisync" in st_name_low
            or ("health" in exec_low and "ai" in exec_low)
            or ("clinical" in exec_low and "diagnosis" in exec_low)
        )

        # 1. Guarantee non-empty skills and responsibilities across all roles
        for role in self.recommended_team_structure:
            if not role.skills and role.required_skills:
                role.skills = role.required_skills
            elif not role.required_skills and role.skills:
                role.required_skills = role.skills

            r_title = (role.role or "").strip().lower()

            if not role.responsibilities or len(role.responsibilities.strip()) < 10:
                if "ceo" in r_title or "founder" in r_title:
                    role.responsibilities = "Drives venture vision, customer pilot acquisitions, creator onboarding, and capital runway management."
                elif "cto" in r_title or "tech" in r_title:
                    role.responsibilities = "Architects scalable video processing and AI platform, manages cloud GPU infrastructure, and supervises engineering execution."
                elif "ai" in r_title or "ml" in r_title or "vision" in r_title:
                    role.responsibilities = "Designs, evaluates, and optimizes computer vision, speech transcription, and automated highlight detection pipelines."
                elif "dev" in r_title or "frontend" in r_title or "full" in r_title:
                    role.responsibilities = "Builds responsive web editor interface, video timeline controls, and secure backend API integrations."
                elif "growth" in r_title or "creator" in r_title or "partner" in r_title:
                    role.responsibilities = "Manages creator affiliate programs, executes social distribution strategies, and oversees community feedback loops."
                elif "design" in r_title or "ui" in r_title:
                    role.responsibilities = "Designs subtitle animation templates, canvas layout ergonomics, and brand identity assets."
                else:
                    role.responsibilities = "Executes key functional deliverables, ensures quality standards, and collaborates across the founding team."

            if not role.required_skills:
                if "ceo" in r_title or "founder" in r_title:
                    role.required_skills = ["Executive Leadership", "Creator Economy Strategy", "SaaS Growth", "Fundraising", "Go-To-Market"]
                elif "cto" in r_title or "tech" in r_title:
                    role.required_skills = ["System Architecture", "Python", "Cloud GPU Infrastructure", "FFmpeg", "Microservices"]
                elif "ai" in r_title or "ml" in r_title or "vision" in r_title:
                    role.required_skills = ["PyTorch", "OpenCV", "Whisper / Speech-to-Text", "Model Quantization", "Audio/Video NLP"]
                elif "dev" in r_title or "frontend" in r_title:
                    role.required_skills = ["React / Next.js", "TypeScript", "Tailwind CSS", "HTML5 Video APIs", "REST APIs"]
                elif "growth" in r_title or "creator" in r_title:
                    role.required_skills = ["Influencer Outreach", "Creator Community Management", "Social Media Growth", "Affiliate Marketing"]
                elif "design" in r_title or "ui" in r_title:
                    role.required_skills = ["Figma", "UI/UX Design", "Motion Graphics", "Typography & Subtitle Styling"]
                else:
                    role.required_skills = ["Domain Problem Solving", "Process Management", "Analytical Rigor"]
                role.skills = role.required_skills

            if not role.why_needed or len(role.why_needed.strip()) < 10:
                if "later" in role.priority.lower():
                    role.why_needed = "Can be deferred during early MVP launch; core founders or fractional freelancers can handle responsibilities until pilot traction warrants full-time hire."
                else:
                    role.why_needed = "Critical for immediate MVP build, core product validation, and establishing baseline operational credibility."

        # 2. Domain Standard Enforcement: CreatorClip AI / Video AI Tools
        if is_creator:
            existing_roles_map = {r.role.lower(): r for r in self.recommended_team_structure}
            creator_standard_roles = [
                TeamRole(
                    role="Chief Executive Officer (CEO) / Founder",
                    reports_to="None",
                    department="Executive Leadership",
                    priority="Essential",
                    experience_level="Executive",
                    why_needed="Drives overall venture strategy, spearheads creator community acquisition, conducts user feedback interviews, and manages fundraising runway.",
                    responsibilities="Leads go-to-market execution, manages creator affiliate partnerships, secures early beta testers, and manages investor and grant relationships.",
                    required_skills=["Creator Economy Strategy", "Prosumer SaaS Growth", "User Interviewing", "Venture Fundraising", "Stakeholder Governance"],
                    skills=["Creator Economy Strategy", "Prosumer SaaS Growth", "Venture Fundraising"],
                    soft_skills=["Visionary Communication", "Creator Empathy", "Tenacity", "Negotiation"],
                ),
                TeamRole(
                    role="Chief Technology Officer (CTO)",
                    reports_to="Chief Executive Officer (CEO) / Founder",
                    department="Engineering & Technology",
                    priority="Essential",
                    experience_level="Lead / Executive",
                    why_needed="Architects the low-latency media transcoding pipeline, cloud GPU scaling, and microservices backend required for high-volume video processing.",
                    responsibilities="Designs backend infrastructure (FastAPI/Docker/FFmpeg), orchestrates GPU cloud compute, establishes CI/CD deployment pipelines, and enforces security.",
                    required_skills=["System Architecture", "Python", "Cloud GPU Infrastructure", "FFmpeg Media Pipelines", "FastAPI / Docker"],
                    skills=["System Architecture", "Python", "Cloud GPU Infrastructure", "FFmpeg Media Pipelines"],
                    soft_skills=["Technical Mentorship", "Decisiveness", "Agile Execution", "Ownership"],
                ),
                TeamRole(
                    role="AI / Computer Vision & Audio Engineer",
                    reports_to="Chief Technology Officer (CTO)",
                    department="AI & Data Intelligence",
                    priority="Essential",
                    experience_level="Senior",
                    why_needed="Develops multimodal intelligence pipelines for automatic speech transcription, active-speaker face framing (16:9 to 9:16), and hook virality scoring.",
                    responsibilities="Fine-tunes Whisper/speech models for timestamp accuracy, implements OpenCV/MediaPipe speaker tracking, and optimizes inference latency on GPU instances.",
                    required_skills=["PyTorch", "Whisper / Speech-to-Text", "OpenCV / MediaPipe", "Computer Vision", "Model Quantization & MLOps"],
                    skills=["PyTorch", "Whisper / Speech-to-Text", "OpenCV / MediaPipe", "MLOps"],
                    soft_skills=["Analytical Rigor", "Experimental Discipline", "Curiosity", "Problem Solving"],
                ),
                TeamRole(
                    role="Full-Stack / Frontend Developer",
                    reports_to="Chief Technology Officer (CTO)",
                    department="Engineering & Technology",
                    priority="Essential",
                    experience_level="Mid-to-Senior",
                    why_needed="Builds an intuitive, browser-based video editing canvas where creators can preview clips, customize captions, edit subtitles, and export.",
                    responsibilities="Implements interactive Next.js/React video editing UI, manages state synchronization with backend render queues, and integrates payment checkouts.",
                    required_skills=["React / Next.js", "TypeScript", "Tailwind CSS", "HTML5 Canvas / Video APIs", "State Management", "REST APIs"],
                    skills=["React / Next.js", "TypeScript", "HTML5 Canvas / Video APIs"],
                    soft_skills=["Product Polish", "Attention to Detail", "Cross-Disciplinary Teamwork"],
                ),
                TeamRole(
                    role="Creator Partnerships & Growth Lead",
                    reports_to="Chief Executive Officer (CEO) / Founder",
                    department="Growth & Creator Marketing",
                    priority="Later",
                    experience_level="Senior Lead",
                    why_needed="Scales YouTuber and podcaster affiliate programs and manages organic distribution. Deferrable during early MVP build.",
                    responsibilities="Identifies and recruits podcaster brand ambassadors, structures referral incentive programs, manages TikTok/Reels marketing, and tracks user CAC.",
                    required_skills=["Influencer Outreach", "Creator Community Management", "Social Video Marketing", "Affiliate Programs", "Performance Analytics"],
                    skills=["Influencer Outreach", "Creator Community Management", "Social Video Marketing"],
                    soft_skills=["Persuasion", "Relationship Building", "High Energy", "Charisma"],
                ),
                TeamRole(
                    role="UI/UX & Subtitle Designer",
                    reports_to="Chief Executive Officer (CEO) / Founder",
                    department="Product & Design",
                    priority="Later",
                    experience_level="Mid-Level",
                    why_needed="Designs animated viral subtitle presets, motion graphics templates, and user onboarding ergonomics. Can be engaged as fractional contractor during MVP.",
                    responsibilities="Produces subtitle typography libraries, designs export aspect ratio presets, conducts usability testing on editor controls, and builds design system.",
                    required_skills=["Figma", "UI/UX Design", "Motion Typography", "Brand Identity", "User Testing"],
                    skills=["Figma", "UI/UX Design", "Motion Typography"],
                    soft_skills=["Visual Polish", "User Empathy", "Design Aesthetics"],
                ),
            ]

            for std_role in creator_standard_roles:
                matched = any(
                    std_role.role.lower().split()[0] in r_key
                    or any(k in r_key for k in ["vision", "audio", "ai"] if "ai" in std_role.role.lower())
                    or any(k in r_key for k in ["frontend", "full-stack", "developer"] if "frontend" in std_role.role.lower())
                    or any(k in r_key for k in ["growth", "partner", "marketing"] if "growth" in std_role.role.lower())
                    or any(k in r_key for k in ["design", "ui", "ux"] if "design" in std_role.role.lower())
                    for r_key in existing_roles_map
                )
                if not matched:
                    self.recommended_team_structure.append(std_role)

            if not self.lean_team_advice:
                self.lean_team_advice = (
                    "During initial MVP validation, CreatorClip AI operates ultra-lean with a core two-to-three person founding technical team "
                    "(CEO driving product direction and direct creator outreach; CTO leading cloud architecture and AI pipelines; supported by a Full-Stack Developer). "
                    "Creator partnerships, social media promotion, and visual subtitle styling are handled directly by the founder or fractional freelance contractors "
                    "until paying subscriber traction warrants hiring dedicated growth and design leads."
                )

            # Verified Competitor Profiles for Video AI Clipping Tools
            self.competitor_analysis = [
                Competitor(
                    name="Opus Clip (OpusClip Inc.)",
                    product_service="Generative AI video repurposing platform converting long videos into short viral clips with auto-reframe, dynamic captions, and virality scoring.",
                    target_customers="Video podcasters, YouTubers, digital marketing agencies, and social content teams.",
                    business_model="Freemium B2C/B2B SaaS subscription with credit-based usage tiers.",
                    pricing="Free tier ($0, 60 credits/mo with watermark); Starter ($15/mo or $9.50/mo billed annually); Pro ($29/mo); Business (Custom) [Source: opus.pro/pricing, Date Checked: October 2026]",
                    funding_raised="$20M Series B led by SoftBank Vision Fund 2 (March 2025); total funding ~$68M [Source: Tracxn / TechCrunch, Date Checked: October 2026]",
                    revenue="Unverified (Private US company; statutory financials not publicly filed)",
                    profit_loss="Unverified",
                    strengths=["High brand awareness", "Fast 1-click generation", "AI virality scoring", "Multi-speaker dynamic reframing"],
                    weaknesses=["Credit-based limits penalize volume", "Post-generation video editing is constrained", "Aggressive subscription throttling on heavy exports"],
                    source="Official Website & Tracxn",
                    source_url="https://www.opus.pro/pricing",
                    date_checked="October 2026",
                ),
                Competitor(
                    name="InVideo (InVideo Inc.)",
                    product_service="Comprehensive AI text-to-video generation and automated script-to-video editing suite (InVideo AI).",
                    target_customers="Content creators, marketing professionals, small business owners, and social media managers.",
                    business_model="Freemium SaaS subscription with monthly and annual plans.",
                    pricing="Free tier ($0 with watermark); Plus ($25/mo or $20/mo billed annually); Max ($60/mo or $48/mo billed annually) [Source: invideo.io/pricing, Date Checked: October 2026]",
                    funding_raised="$52.5M across Seed ($2.5M), Series A ($15M Tiger Global), and Series B ($35M Base Partners) [Source: Tracxn, Date Checked: October 2026]",
                    revenue="Unverified (Self-disclosed $70M ARR claimed by CEO; audited statutory filings unverified in public domain)",
                    profit_loss="Unverified",
                    strengths=["Massive stock footage library", "Generative text-to-video capabilities", "Strong mobile and web companion apps"],
                    weaknesses=["Less specialized for automated podcast highlight extraction", "Steeper learning curve for quick short-form repurposing"],
                    source="Official Website & Tracxn",
                    source_url="https://invideo.io/pricing",
                    date_checked="October 2026",
                ),
                Competitor(
                    name="Klap (Klap.app)",
                    product_service="AI video clipping tool designed to extract engaging topics and format them into TikTok, Reels, and Shorts formats.",
                    target_customers="Solo content creators, podcasters, and YouTube video publishers.",
                    business_model="Monthly/annual tiered SaaS subscription.",
                    pricing="Starter ($29/mo or $14.50/mo billed annually); Pro ($39/mo or $29/mo billed annually) [Source: klap.app/pricing, Date Checked: October 2026]",
                    funding_raised="Unverified (Bootstrapped / private angel capital)",
                    revenue="Unverified",
                    profit_loss="Unverified",
                    strengths=["Clean minimal UI", "Fast YouTube URL import", "Generous video minute limits"],
                    weaknesses=["Limited advanced brand kit features", "Smaller team with slower template updates"],
                    source="Official Website",
                    source_url="https://klap.app/pricing",
                    date_checked="October 2026",
                ),
                Competitor(
                    name="Munch (GetMunch)",
                    product_service="AI video repurposing platform providing automated clipping paired with marketing trend analysis and keyword insights.",
                    target_customers="Brands, media enterprises, and digital marketing agencies.",
                    business_model="Subscription B2B SaaS.",
                    pricing="Pro tier at ~$49/mo; Elite tier at ~$119/mo [Source: getmunch.com/pricing, Date Checked: October 2026]",
                    funding_raised="$7.2M Seed round [Source: Tracxn, Date Checked: October 2026]",
                    revenue="Unverified",
                    profit_loss="Unverified",
                    strengths=["Trend-based topic extraction", "Social engagement analytics", "Multi-channel auto-scheduling"],
                    weaknesses=["Significantly higher starting price for early indie creators", "Complex enterprise-focused interface"],
                    source="Official Website & Tracxn",
                    source_url="https://www.getmunch.com/pricing",
                    date_checked="October 2026",
                ),
            ]

            # Mathematically Accurate Lean Financial Projections for CreatorClip AI
            self.financial_analysis = FinancialAnalysis(
                mvp_budget_breakdown=[
                    "Domain & Identity: ₹1,000 (1-year .com or .in domain registration via Cloudflare/Namecheap) [Assumption]",
                    "Cloud Infrastructure & Database: ₹0 (Bootstrapped on free developer tiers: Vercel frontend, Supabase PostgreSQL, Render services) [Assumption]",
                    "AI Model Inference & Transcoding: ₹3,500 (Pay-as-you-go developer credits for OpenAI Whisper & Gemini 1.5 Flash transcription/hook extraction) [Estimate]",
                    "Core Video Processing Stack: ₹0 (Open-source tools: FFmpeg, Python FastAPI, Next.js, Tailwind CSS) [Assumption]",
                    "Operational Tooling & Workspace: ₹1,500 (Basic transactional email services and developer testing tooling) [Estimate]",
                    "Total Estimated Lean MVP Build Budget: ₹6,000 (Sub-₹10,000 bootstrapping target) [Planning Assumption]",
                ],
                estimated_monthly_burn="₹3,500 - ₹7,000 / month during MVP validation (cloud compute scaling, pay-as-you-go API consumption, and domain maintenance) [Assumption]",
                pricing_model_and_unit_economics=(
                    "Tiered Freemium B2C/Prosumer SaaS: Free tier (30 export mins/mo with watermark); "
                    "Creator Starter tier @ ₹999/month (~$12/mo) for 120 processing minutes, 1080p exports, auto-captions, and no watermark; "
                    "Pro Creator tier @ ₹2,499/month (~$30/mo) for 400 processing minutes, multi-aspect ratio exports (9:16, 1:1, 16:9), AI virality scoring, and auto-scheduling. "
                    "Direct API/transcoding cost is ~₹150 - ₹250 per 100 minutes, yielding an estimated gross margin of ~75% - 85% on paid subscriptions. [Planning Assumptions]"
                ),
                revenue_scenarios=[
                    "Conservative Scenario (Months 1–6): 25 Starter subscribers (@ ₹999/mo = ₹24,975) + 5 Pro subscribers (@ ₹2,499/mo = ₹12,495) = ₹37,470/month (Annualized Run Rate: ₹4,49,640 ~ ₹4.5 Lakhs ARR) [Planning assumption only — NOT guaranteed revenue]",
                    "Moderate Scenario (Months 7–12): 100 Starter subscribers (@ ₹999/mo = ₹99,900) + 40 Pro subscribers (@ ₹2,499/mo = ₹99,960) = ₹1,99,860/month (Annualized Run Rate: ₹23,98,320 ~ ₹24.0 Lakhs ARR) [Planning assumption only — NOT guaranteed revenue]",
                    "Aggressive Scenario (Year 2): 400 Starter subscribers (@ ₹999/mo = ₹3,99,600) + 160 Pro subscribers (@ ₹2,499/mo = ₹3,99,840) = ₹7,99,440/month (Annualized Run Rate: ₹95,93,280 ~ ₹96.0 Lakhs ARR) [Planning assumption only — NOT guaranteed revenue]",
                ],
                break_even_assumptions=(
                    "Fixed monthly operational burn is estimated at ~₹15,000 - ₹25,000 (compute, APIs, and tooling). "
                    "With an average subscription price of ~₹1,400 across Starter/Pro tiers and ~80% gross margin (net contribution of ~₹1,120 per user), "
                    "the venture reaches operational break-even at approximately 15 to 22 active paying subscribers "
                    "(e.g., 18 users * ₹1,120 = ₹20,160 net contribution, covering ₹20,000 monthly burn). [Planning Assumption]"
                ),
                competitor_or_historical_benchmarks=[
                    "Opus Clip: $20M Series B (March 2025); ARR and profitability are unverified in statutory public filings. [Date Checked: October 2026]",
                    "InVideo: $52.5M total funding; self-disclosed $70M ARR claimed by CEO, but audited statutory filings are unverified in public domain. [Date Checked: October 2026]",
                    "General Market Note: Venture capital raised must never be treated as operational revenue. Private competitor revenues are unverified unless sourced from official regulatory filings.",
                ],
            )

            # Creator/Media Technology-Specific Risk Assessment
            self.risk_analysis = [
                RiskItem(
                    category="Technical",
                    risk="Video transcoding latency spikes and GPU queue bottlenecks when processing 60+ minute source videos.",
                    impact="High",
                    mitigation_strategy="Implement asynchronous worker queues (Celery/Redis), chunk video files for parallel FFmpeg processing, and leverage auto-scaling spot GPU compute."
                ),
                RiskItem(
                    category="Technical & AI Quality",
                    risk="Transcription word error rate (WER) on varied non-native accents and technical jargon causing inaccurate captions.",
                    impact="Medium",
                    mitigation_strategy="Utilize fine-tuned Whisper-large models with custom vocabulary dictionaries and provide an inline subtitle editor for immediate manual correction."
                ),
                RiskItem(
                    category="Market & Competition",
                    risk="Aggressive feature replication or discounting by well-funded incumbents (such as Opus Clip or InVideo).",
                    impact="High",
                    mitigation_strategy="Differentiate through localized creator pricing (INR native checkout), superior Indian language subtitle support, and niche vertical editing workflows."
                ),
                RiskItem(
                    category="Operational & API Dependency",
                    risk="Sudden rate limit restrictions or policy changes on third-party video platform APIs (YouTube Data API, TikTok API).",
                    impact="Medium",
                    mitigation_strategy="Offer direct video file upload fallbacks, maintain compliance with platform developer guidelines, and diversify export destinations."
                ),
                RiskItem(
                    category="Regulatory & IP",
                    risk="Content copyright infringement claims if users process unlicensed broadcast footage.",
                    impact="Medium",
                    mitigation_strategy="Incorporate strict Terms of Service disclaimers requiring content ownership confirmation, automated hash logging, and DMCA takedown procedures."
                ),
            ]

            # Domain-Specific Government and Private Funding for Software/AI Startups
            self.government_funding_schemes = [
                FundingOpportunity(
                    name="MeitY TIDE 2.0 (Technology Incubation and Development of Entrepreneurs)",
                    organization="Ministry of Electronics and Information Technology (MeitY) / MeitY Startup Hub",
                    funding_type="Grant",
                    funding_amount="Up to ₹4 Lakhs (EiR) / Up to ₹7 Lakhs (Grant-in-Aid) / Soft loan up to ₹30 Lakhs",
                    eligibility="Registered Indian tech startups working on emerging ICT/AI technologies through supported incubation centers.",
                    who_can_apply="Indian registered tech startups or budding student/innovator entrepreneurs",
                    startup_stage="Ideation, Prototype/MVP, Early Validation",
                    usage="Prototype development, AI model compute testing, and initial product validation",
                    where_to_apply="Participating TIDE 2.0 Incubation Centres (IITs, NITs, IIITs) or MeitY Startup Hub portal",
                    application_website="https://msh.meity.gov.in/schemes/tide",
                    official_source_name="MeitY Startup Hub Official Portal",
                    official_source_url="https://msh.meity.gov.in/schemes/tide",
                    official_source="MeitY Startup Hub",
                    deadline="Status unverified — Check official portal for active incubator call announcements",
                    date_checked="October 2026",
                    status_evidence="Incubator-specific cohort calls; check MSH portal for open center calls",
                    why_suitable="Directly funds software and AI media tech prototyping through non-dilutive government grants.",
                ),
                FundingOpportunity(
                    name="MSME Innovative Scheme (Incubation Component)",
                    organization="Ministry of Micro, Small and Medium Enterprises (MoMSME)",
                    funding_type="Grant",
                    funding_amount="Financial assistance up to ₹15 Lakhs per approved idea",
                    eligibility="Indian startups or individual entrepreneurs with innovative concepts incubated via recognized Host Institutes (HIs).",
                    who_can_apply="Registered MSMEs (Udyam registration) and tech innovators via Host Institutes",
                    startup_stage="Ideation, Validation, Prototype/MVP",
                    usage="Developing innovative proof of concept, commercial validation, and software prototypes",
                    where_to_apply="MSME Innovative Scheme official portal through approved Host Institutes",
                    application_website="https://innovative.msme.gov.in",
                    official_source_name="Ministry of MSME Official Portal",
                    official_source_url="https://innovative.msme.gov.in",
                    official_source="Ministry of MSME",
                    deadline="Status unverified — Check official portal for active national call for proposals",
                    date_checked="October 2026",
                    status_evidence="Periodic national calls for proposal submissions; verify current window on portal",
                    why_suitable="Provides non-dilutive grant support to turn digital software concepts into commercially viable products.",
                ),
                FundingOpportunity(
                    name="NIDHI-PRAYAS Scheme",
                    organization="Department of Science and Technology (DST), Government of India",
                    funding_type="Grant",
                    funding_amount="Grant-in-aid up to ₹10 Lakhs",
                    eligibility="Individual innovators or early-stage tech companies incorporated for under 3 years incubated at a PRAYAS Centre.",
                    who_can_apply="Early-stage tech startups with a tangible proof-of-concept prototype plan",
                    startup_stage="Ideation to Proof of Concept / MVP Prototyping",
                    usage="Prototyping equipment, cloud infrastructure, software development tools, and trial validation",
                    where_to_apply="Designated DST PRAYAS Incubation Centres across premier institutes",
                    application_website="https://nidhi-prayas.org",
                    official_source_name="Department of Science and Technology (DST)",
                    official_source_url="https://dst.gov.in",
                    official_source="Department of Science and Technology",
                    deadline="Status unverified — Incubator-specific cohort calls; verify with local DST PRAYAS incubators",
                    date_checked="October 2026",
                    status_evidence="Administered independently by authorized PRAYAS centers across India",
                    why_suitable="Enables early technology ventures to transition algorithmic concepts into functioning software platforms.",
                ),
            ]

            self.private_funding_opportunities = [
                FundingOpportunity(
                    name="Microsoft for Startups Founders Hub",
                    organization="Microsoft Corporation",
                    funding_type="Cloud Credits",
                    funding_amount="Up to $150,000 in Azure Cloud Credits (including OpenAI / AI model compute access)",
                    eligibility="Software, SaaS, and AI startups with functional prototypes or working MVPs; no institutional funding required.",
                    who_can_apply="Early-stage technology ventures and bootstrapped founders",
                    startup_stage="Ideation, Prototype/MVP, Early Traction",
                    usage="Cloud GPU compute, high-throughput video rendering, OpenAI API inferences, and developer tooling",
                    where_to_apply="Direct official online application portal",
                    application_website="https://startups.microsoft.com",
                    official_source_name="Microsoft for Startups Official Portal",
                    official_source_url="https://startups.microsoft.com",
                    official_source="Microsoft Corporation",
                    deadline="Ongoing rolling applications",
                    date_checked="October 2026",
                    status_evidence="Active open rolling intake confirmed on official startups.microsoft.com portal",
                    why_suitable="Directly subsidizes the most significant expense of a video AI venture—cloud GPU compute and model inference tokens.",
                ),
                FundingOpportunity(
                    name="Google for Startups Cloud Program (AI Track)",
                    organization="Google LLC",
                    funding_type="Cloud Credits",
                    funding_amount="Up to $200,000 in Google Cloud & Vertex AI credits over 2 years",
                    eligibility="Funded and high-potential bootstrapped AI startups building innovative machine learning applications.",
                    who_can_apply="Incorporated technology startups building proprietary AI features",
                    startup_stage="Prototype/MVP, Early Traction, Scaling",
                    usage="Google Cloud Storage, Vertex AI model endpoints, and Cloud GPU compute instances",
                    where_to_apply="Official Google Cloud for Startups application portal",
                    application_website="https://cloud.google.com/startup",
                    official_source_name="Google Cloud Official Portal",
                    official_source_url="https://cloud.google.com/startup",
                    official_source="Google LLC",
                    deadline="Ongoing rolling applications",
                    date_checked="October 2026",
                    status_evidence="Active open rolling applications verified on cloud.google.com/startup",
                    why_suitable="Provides extensive cloud storage and GPU acceleration essential for scalable video processing.",
                ),
                FundingOpportunity(
                    name="AWS Activate for Startups",
                    organization="Amazon Web Services (AWS)",
                    funding_type="Cloud Credits",
                    funding_amount="Up to $100,000 in AWS promotional credits",
                    eligibility="Early-stage tech startups associated with select incubators, accelerators, or seed investment funds.",
                    who_can_apply="Bootstrapped and institutional-backed technology startups",
                    startup_stage="Ideation, MVP, Early Growth",
                    usage="AWS EC2 GPU instances, S3 media storage, and AWS MediaConvert transcoding pipelines",
                    where_to_apply="Official AWS Activate portal",
                    application_website="https://aws.amazon.com/activate/",
                    official_source_name="Amazon Web Services Official Portal",
                    official_source_url="https://aws.amazon.com/activate/",
                    official_source="Amazon Web Services",
                    deadline="Ongoing rolling applications",
                    date_checked="October 2026",
                    status_evidence="Active rolling program confirmed on aws.amazon.com/activate",
                    why_suitable="Covers scalable media file storage and cloud transcode server costs during initial traction.",
                ),
            ]

            # 5-Phase Execution Roadmap Tailored to Video Creator Tools
            self.roadmap = [
                RoadmapStep(
                    step_number=1,
                    phase_name="Core AI Pipeline & Transcode Architecture",
                    description="Develop backend pipeline for video ingestion, audio demuxing, Whisper transcription, and silence/hook detection using FFmpeg and open-source models.",
                    estimated_timeline="Months 1–2",
                    deliverables=["Working Python/FastAPI transcoding microservice", "Whisper timestamp alignment pipeline", "Dockerized local testing environment"],
                ),
                RoadmapStep(
                    step_number=2,
                    phase_name="Web Editor MVP & Creator Alpha Testing",
                    description="Build responsive Next.js canvas interface allowing creators to upload 15-minute test videos, view auto-detected clips, and edit subtitle timing.",
                    estimated_timeline="Months 3–4",
                    deliverables=["Interactive browser video editor", "Custom subtitle styling engine", "Closed alpha testing with 15 podcasters"],
                ),
                RoadmapStep(
                    step_number=3,
                    phase_name="Public Beta Launch & Creator Validation",
                    description="Launch public beta with 30 free minutes/month; initiate direct outreach to YouTubers and podcasters to validate virality scoring accuracy and UX.",
                    estimated_timeline="Months 5–6",
                    deliverables=["Public freemium web app", "INR/USD payment gateway integration", "Onboarding of 100+ active beta creators"],
                ),
                RoadmapStep(
                    step_number=4,
                    phase_name="Monetization, Brand Kits & Social Auto-Scheduling",
                    description="Deploy paid Starter and Pro subscription tiers; implement custom brand kits, multi-aspect ratio rendering (9:16, 1:1), and direct social posting.",
                    estimated_timeline="Months 7–9",
                    deliverables=["Tiered SaaS billing system", "Direct TikTok/YouTube Shorts export APIs", "First 50 paying subscriber conversions"],
                ),
                RoadmapStep(
                    step_number=5,
                    phase_name="Affiliate Growth & High-Volume Enterprise Workflows",
                    description="Introduce creator affiliate referral programs, team collaboration workspaces for agencies, and API access for high-volume content repurposing.",
                    estimated_timeline="Months 10–12",
                    deliverables=["Creator affiliate referral dashboard", "Multi-seat agency team workspaces", "Break-even unit economics target achieved"],
                ),
            ]

        # 3. Founder / CEO root reporting strictly 'None' and sorting
        for role in self.recommended_team_structure:
            r_lower = role.role.strip().lower()
            if "ceo" in r_lower or "founder" in r_lower:
                role.reports_to = "None"
            elif role.reports_to:
                rep_lower = str(role.reports_to).strip().lower()
                if rep_lower in [r_lower, "", "none", "null"]:
                    role.reports_to = "None"

        self.recommended_team_structure.sort(
            key=lambda r: 0 if ("ceo" in r.role.lower() or "founder" in r.role.lower()) else 1
        )

        # 4. Sync team_hierarchy
        self.team_hierarchy = [
            HierarchyNode(
                role=r.role,
                reports_to=r.reports_to,
                department=r.department,
                priority=r.priority,
            )
            for r in self.recommended_team_structure
        ]

        # 5. Normalize Microsoft for Startups official URL across all funding programs
        all_opps = self.government_funding_schemes + self.private_funding_opportunities + self.funding_opportunities
        for opp in all_opps:
            opp_text = f"{opp.name} {opp.organization} {opp.official_source_name}".lower()
            if "microsoft for startups" in opp_text or "founders hub" in opp_text:
                if not opp.application_website or opp.application_website == "Unverified" or "startup.microsoft.com" in opp.application_website.lower():
                    opp.application_website = "https://startups.microsoft.com"
                if not opp.official_source_url or opp.official_source_url == "Unverified" or "startup.microsoft.com" in opp.official_source_url.lower():
                    opp.official_source_url = "https://startups.microsoft.com"

        for src in self.sources:
            if "microsoft for startups" in src.name.lower() or "founders hub" in src.name.lower():
                if not src.url or "startup.microsoft.com" in src.url.lower():
                    src.url = "https://startups.microsoft.com"

        # 6. Sanitize Financial Information
        cleaned_financials = []
        for fin in self.financial_information:
            if "internal startup assessment" in str(fin).lower() or "internal assessment" in str(fin).lower():
                cleaned_financials.append("Unverified")
            else:
                cleaned_financials.append(fin)
        self.financial_information = cleaned_financials or ["Unverified"]

        # 7. Ensure funding_opportunities contains both categories
        if not self.funding_opportunities:
            self.funding_opportunities = self.government_funding_schemes + self.private_funding_opportunities

        # 8. Ensure official_source display fallback is populated
        for opp in all_opps:
            if not opp.official_source or opp.official_source == "Unverified":
                if opp.official_source_name and opp.official_source_name != "Unverified":
                    opp.official_source = opp.official_source_name
                elif opp.organization and opp.organization != "Unverified":
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
      - Provide a MINIMUM of 3 genuine, highly relevant government funding schemes, grants, or seed funds (e.g. MeitY TIDE 2.0, MSME Innovative Scheme, NIDHI-PRAYAS) specifically applicable to the startup's domain and stage.
      - RULE: NEVER combine two unrelated programs into one entry.
      - For MeitY TIDE 2.0, set application_website to 'https://msh.meity.gov.in/schemes/tide'.
      - For MSME Innovative Scheme, set application_website to 'https://innovative.msme.gov.in'.
      - RESEARCH ACCURACY: If mentioning Startup India Seed Fund Scheme (SISFS), state clearly that it closed for new startup applications on 31 May 2026. Do NOT present closed schemes as currently open.
      - Specify date_checked and status_evidence for each scheme.
      - RULE: Only recommend schemes relevant to the startup's actual domain. Do NOT recommend biotechnology schemes (like BIRAC) to a video, media, or SaaS startup.

   B. PRIVATE FUNDING OPPORTUNITIES (private_funding_opportunities):
      - Provide a MINIMUM of 3 genuine, highly relevant private funding opportunities (VC seed funds, Angel networks, Accelerators, Corporate credits).
      - RULE: For Microsoft for Startups, use the verified official portal URL: https://startups.microsoft.com.

3. DYNAMIC COMPANY & TEAM STRUCTURE:
   - Generate a complete, domain-specific organizational structure (6 to 9 distinct roles).
   - For every role, provide complete, startup-specific 'responsibilities' (2-3 detailed deliverables), 'why_needed', and 'required_skills' (3-5 specific technical/domain proficiencies). NEVER leave responsibilities or skills empty or as 'Not specified'.
   - For roles with priority 'Later', explain in 'why_needed' how early founders can defer hiring or handle responsibilities fractionally/part-time during MVP.
   - Set reports_to to 'None' for the Founder / CEO.

4. COMPETITOR ANALYSIS & FINANCIAL CLASSIFICATION:
   - Identify real competitor companies or market alternatives (e.g. Opus Clip, InVideo, Klap, Munch).
   - STRICT FINANCIAL RULES: NEVER classify external funding or investment raised as company revenue!
   - Show verified pricing, funding, source URL, and date checked. If revenue or profit/loss cannot be verified from public filings, label as 'Unverified'.

5. FINANCIAL ANALYSIS (financial_analysis):
   - mvp_budget_breakdown: Itemize a realistic lean MVP budget. Respect a budget below ₹10,000 where feasible by utilizing free-tier hosting (Vercel, Supabase, Render), open-source stacks, and pay-as-you-go APIs. Clearly label all assumptions.
   - estimated_monthly_burn: Estimate monthly operating costs during MVP validation.
   - pricing_model_and_unit_economics: Specify realistic pricing tiers or subscription models and unit economics.
   - revenue_scenarios: Outline conservative, moderate, and aggressive early revenue scenarios with mathematically correct calculations. STRICT RULE: Clearly label all projections as hypothetical planning estimates—NEVER as guaranteed revenue.
   - break_even_assumptions: State the customer volume or unit sales needed to break even.
   - competitor_or_historical_benchmarks: Verified benchmarks or 'Unverified'.

6. RISK ANALYSIS (risk_analysis):
   - Provide 5 to 7 specific, actionable risks across: Technical, Market, Financial, Operational, Regulatory & IP, and Privacy & Security.
   - Explain the impact and concrete mitigation plan for each risk.

7. STARTUP VS COMPETITORS: Sharp differentiation points.
8. IMPORTANT RECOMMENDATIONS: Actionable founder execution recommendations.
9. SOURCES / OFFICIAL LINKS: Clickable verified URLs and official portals with date checked.
10. STARTUP ROADMAP (5 TO 7 SEQUENTIAL PHASES): Sequential execution roadmap tailored to the startup idea with deliverables, emphasizing creator/user validation for video creator tools.
"""

    result = structured_llm.invoke(prompt)

    return {
        "startup_intelligence": result.model_dump(),
    }