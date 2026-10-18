import os
import sys
import re
import zlib

# Ensure current and parent backend modules are importable
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
for p in [current_dir, parent_dir]:
    if p not in sys.path:
        sys.path.insert(0, p)

from pdf_generator import (
    generate_startup_intelligence_pdf,
    build_multi_level_hierarchy_diagram,
    get_opportunity_status,
    sanitize_sisfs_and_msme_recommendation,
)


# ============================================================================
# STARTUP FIXTURE 1: AI HEALTHCARE STARTUP (MEDAI DIAGNOSTICS)
# ============================================================================

def get_healthcare_startup_data():
    return {
        "startup_name": "MedAI Diagnostics",
        "industry": "Healthcare AI & Clinical MedTech",
        "stage": "Clinical Validation & Prototype Trials",
        "executive_summary": (
            "MedAI Diagnostics is an AI-first automated radiology triage platform "
            "designed to assist hospital emergency departments and diagnostic chains "
            "in detecting critical neurovascular and pulmonary anomalies in CT/X-ray scans in under 90 seconds."
        ),
        "startup_idea_and_business_model": {
            "value_proposition": "Sub-90-second automated triage for brain hemorrhage and pneumothorax on edge PACS servers.",
            "target_customers": "Tertiary hospital emergency rooms, radiologist teleradiology networks, and national diagnostic chains.",
            "revenue_model": "Per-scan automated audit fee ($2.00-$3.50/scan) combined with annual hospital software deployment licenses.",
            "go_to_market": "Retrospective hospital clinical audits, ethical committee approvals, and DICOM PACS vendor integrations."
        },
        "government_funding_schemes": [
            {
                "name": "Startup India Seed Fund Scheme (SISFS)",
                "organization": "Department for Promotion of Industry and Internal Trade (DPIIT)",
                "funding_type": "Grant / Convertible Debentures",
                "funding_amount": "Up to ₹20 Lakhs (Proof of Concept) / Up to ₹50 Lakhs (Commercialization)",
                "startup_stage": "Early Stage / Validation & Prototype",
                "deadline": "Ongoing",  # Passed as Ongoing to verify override to CLOSED
                "eligibility": "DPIIT-recognized healthtech startup incorporated not more than 2 years ago.",
                "who_can_apply": "Founders with working radiology prototype ready for clinical hospital trials.",
                "permitted_fund_usage": "Clinical trials, validation datasets, and ISO 13485 certification.",
                "why_suitable": "Provides non-dilutive seed capital for clinical trials.",
                "where_to_apply": "Startup India Official National Portal",
                "application_website": "https://seedfund.startupindia.gov.in",
                "official_source_name": "DPIIT Startup India Portal",
                "official_source_url": "https://seedfund.startupindia.gov.in",
                "application_steps": ["Register entity on Startup India.", "Apply to empaneled healthcare incubators."],
                "required_documents": ["DPIIT Recognition Certificate", "Clinical Protocol Deck"]
            },
            {
                "name": "Biotechnology Ignition Grant (BIG)",
                "organization": "Biotechnology Industry Research Assistance Council (BIRAC)",
                "funding_type": "Grant-in-aid (Non-dilutive)",
                "funding_amount": "Up to ₹50 Lakhs",
                "startup_stage": "Proof of Concept / Early Validation",
                "deadline": "Biannual Call Cycles (typically January and July)",
                "eligibility": "Biotech or MedTech startups with at least 51% Indian shareholding, incorporated under 5 years.",
                "who_can_apply": "Clinical researchers and registered healthtech entities.",
                "permitted_fund_usage": "R&D, hospital clinical testing, and ethical clearance expenses.",
                "why_suitable": "Non-dilutive grant for high-risk medical AI validation.",
                "where_to_apply": "BIRAC Online Portal through C-CAMP / FITT",
                "application_website": "https://birac.nic.in",
                "official_source_name": "BIRAC Government of India",
                "official_source_url": "https://birac.nic.in",
                "application_steps": ["Submit proposal on birac.nic.in during open call."],
                "required_documents": ["Technical Project Proposal", "Clinical Partner Hospital Letter"]
            }
        ],
        "private_funding_opportunities": [
            {
                "name": "Microsoft for Startups Founders Hub",
                "organization": "Microsoft Corporation",
                "funding_type": "Cloud Credits & GPU Clusters",
                "funding_amount": "Up to $150,000 in Azure Cloud & OpenAI Credits",
                "startup_stage": "Idea to Scale",
                "deadline": "Rolling intake",
                "eligibility": "Software startups building proprietary models.",
                "who_can_apply": "Healthcare AI teams requiring HIPAA-compliant cloud infra.",
                "permitted_fund_usage": "GPU compute, DICOM storage, Azure OpenAI API.",
                "why_suitable": "Hosts HIPAA-compliant CT scan inference endpoints.",
                "where_to_apply": "Microsoft for Startups Official Portal",
                "application_website": "https://startups.microsoft.com",
                "official_source_name": "Microsoft Founders Hub",
                "official_source_url": "https://startups.microsoft.com",
                "application_steps": ["Submit profile on startups.microsoft.com."],
                "required_documents": ["Corporate Domain", "Architecture Overview"]
            }
        ],
        "recommended_team_structure": [
            {
                "role": "CEO / Co-Founder",
                "department": "Executive Leadership",
                "reports_to": "",
                "priority": "Essential",
                "experience_level": "8+ years in HealthTech or enterprise hospital sales",
                "why_needed": "Drives hospital partnerships, investor relations, and clinical trials.",
                "responsibilities": "Fundraising, hospital tie-ups, governance.",
                "required_skills": ["Hospital B2B Sales", "Fundraising", "Governance"],
                "soft_skills": ["Executive Presence", "Negotiation"]
            },
            {
                "role": "Chief Medical Officer (CMO)",
                "department": "Clinical Affairs",
                "reports_to": "CEO / Co-Founder",
                "priority": "Essential",
                "experience_level": "10+ years practicing Radiologist",
                "why_needed": "Validates ground-truth clinical annotations and oversees medical ethics reviews.",
                "responsibilities": "Supervising clinical audits, trial design, CDSCO submissions.",
                "required_skills": ["Radiological Diagnostics", "Clinical Trial Protocols", "GCP"],
                "soft_skills": ["Scientific Communication", "Ethics Leadership"]
            },
            {
                "role": "Chief Technology Officer (CTO)",
                "department": "Engineering & AI",
                "reports_to": "CEO / Co-Founder",
                "priority": "Essential",
                "experience_level": "6+ years Deep Learning / Computer Vision",
                "why_needed": "Architects DICOM inference pipeline and on-premise hospital gateway microservices.",
                "responsibilities": "Model training accuracy, latency optimization, PACS integration.",
                "required_skills": ["PyTorch", "Computer Vision", "DICOM Standards", "Docker"],
                "soft_skills": ["Technical Strategy", "Mentorship"]
            },
            {
                "role": "Lead AI Engineer",
                "department": "Engineering & AI",
                "reports_to": "Chief Technology Officer (CTO)",
                "priority": "Essential",
                "experience_level": "4+ years Computer Vision",
                "why_needed": "Develops convolution models for slice-level anomaly segmentation.",
                "responsibilities": "Training models, hyperparameter tuning, latency profiling.",
                "required_skills": ["TensorFlow", "CUDA", "3D ResNet"],
                "soft_skills": ["Execution Speed", "Attention to Detail"]
            },
            {
                "role": "Head of Regulatory Affairs",
                "department": "Compliance",
                "reports_to": "CEO / Co-Founder",
                "priority": "Later (Scale Stage)",
                "experience_level": "5+ years in Medical Device Regulatory Clearances",
                "why_needed": "Drives CDSCO Class C medical software license and FDA 510(k) pathway.",
                "responsibilities": "Managing ISO 13485 audit, technical dossier, compliance submissions.",
                "required_skills": ["CDSCO Medical Device Rules", "FDA 510(k)", "ISO 13485"],
                "soft_skills": ["Regulatory Liaison", "Precision Documentation"]
            }
        ],
        "team_hierarchy": [
            {"role": "CEO / Co-Founder", "reports_to": "", "department": "Executive Leadership", "priority": "Essential"},
            {"role": "Chief Medical Officer (CMO)", "reports_to": "CEO / Co-Founder", "department": "Clinical Affairs", "priority": "Essential"},
            {"role": "Chief Technology Officer (CTO)", "reports_to": "CEO / Co-Founder", "department": "Engineering & AI", "priority": "Essential"},
            {"role": "Lead AI Engineer", "reports_to": "Chief Technology Officer (CTO)", "department": "Engineering & AI", "priority": "Essential"},
            {"role": "Head of Regulatory Affairs", "reports_to": "CEO / Co-Founder", "department": "Compliance", "priority": "Later"}
        ],
        "lean_team_advice": "Focus immediately on the triad of Clinical Leadership (CMO), AI Systems (CTO), and Hospital BizDev (CEO). Defer full-time in-house regulatory counsel to post-seed phase.",
        "competitor_analysis": [
            {
                "name": "Qure.ai",
                "product_service": "AI-powered automated chest X-ray and head CT interpretation.",
                "target_customers": "Large hospital networks and public screening centers.",
                "business_model": "Annual SaaS licensing and per-scan fees.",
                "pricing": "$2.00 - $4.00 per triage scan.",
                "funding_raised": "$70M+ (backed by Novo Holdings, Lightspeed)",
                "revenue": "Estimated ₹120 Cr+ ARR (FY24 filings)",
                "profit_loss": "Operational reinvestment in global clinical clearances",
                "source": "Tracxn, MCA filings",
                "strengths": ["FDA 510(k) clearances", "Deep footprint in 50+ countries"],
                "weaknesses": ["High enterprise switching costs", "Complex bespoke deployment"]
            }
        ],
        "startup_vs_competitors": [
            {"competitor": "Qure.ai", "differentiation": "MedAI operates at 40% lower cost per inference via quantized edge deployment without cloud roundtrip latency."}
        ],
        "financial_analysis": {
            "initial_capital_expenditure": "₹35 Lakhs (Server nodes, anonymized DICOM data licensing, legal audits)",
            "monthly_operating_burn": "₹4.5 Lakhs/month during multi-center hospital pilot validation",
            "projected_break_even": "Month 18 upon onboarding 12 mid-sized hospital emergency chains",
            "funding_requirement": "₹1.5 Cr Seed round for CDSCO trials and PACS engineering expansion"
        },
        "risk_analysis": [
            {"category": "Clinical & Regulatory", "description": "Delays in hospital ethical committee clearance for retrospective clinical audit datasets.", "mitigation": "Partner with 3 distinct tertiary medical colleges to parallelize IRB review."},
            {"category": "Technical Model Liability", "description": "Risk of false negatives in intracranial hemorrhage detection.", "mitigation": "Calibrate high-sensitivity alert threshold (>97%) ensuring radiologist always reviews triage flag."}
        ],
        "roadmap": [
            {
                "step_number": 1,
                "phase_name": "Algorithm Validation & Retrospective Clinical Audit",
                "estimated_timeline": "Months 1 - 4",
                "description": "Train convolution networks on 50,000 anonymized CT scans. Note: apply for Startup India Seed Fund Scheme (SISFS) as ongoing seed capital."  # Raw string to test sanitization
            },
            {
                "step_number": 2,
                "phase_name": "Edge Device PACS Integration & Pilot Rollout",
                "estimated_timeline": "Months 5 - 8",
                "description": "Deploy on-premise inference microservices across 3 partner hospital emergency departments."
            }
        ],
        "important_recommendations": [
            "Apply for the Startup India Seed Fund Scheme (SISFS) - Ongoing as an early-stage non-dilutive grant.",  # Raw string to test sanitization
            "Maintain ongoing clinical trials and ensure ongoing hospital partner feedback is recorded.",  # Unrelated ongoing test
            "Prioritize BIRAC BIG submission with multi-centric clinical hospital validation data."
        ],
        "professional_networks_and_links": [
            {"name": "Qure.ai Official LinkedIn Page", "source_type": "Competitor Profile", "category": "Market Intelligence", "url": "https://www.linkedin.com/company/qure-ai"},
            {"name": "C-CAMP Biotech Incubator", "source_type": "Incubation Partner", "category": "Biotech Grants", "url": "https://www.ccamp.res.in"},
            {"name": "BIRAC BIG Official Scheme Guidelines", "source_type": "Grant Portal", "category": "Funding Guidelines", "url": "https://birac.nic.in"}
        ]
    }


# ============================================================================
# STARTUP FIXTURE 2: AI PERSONAL FINANCE STARTUP (FINWISE AI)
# ============================================================================

def get_personal_finance_startup_data():
    return {
        "startup_name": "FinWise AI",
        "industry": "Personal Finance & Algorithmic WealthTech",
        "stage": "Alpha Prototype & Sandbox Integration",
        "executive_summary": (
            "FinWise AI is an intelligent algorithmic personal finance and wealth mentor "
            "that leverages India's Account Aggregator ecosystem to analyze real-time bank "
            "transactions, optimize discretionary expenditure, and automate tax-loss harvesting."
        ),
        "startup_idea_and_business_model": {
            "value_proposition": "Automated hyper-personalized cash flow forecasting and micro-investment reallocation via RBI Account Aggregators.",
            "target_customers": "Tech professionals and retail salary earners (22-38 years) seeking automated tax optimization and wealth building.",
            "revenue_model": "Freemium tiered subscription (₹199/month Pro tier) + mutual fund distributor trailing commission (AUM-based).",
            "go_to_market": "Fintech community partnerships, organic financial literacy micro-tools, and Account Aggregator onboarding."
        },
        "government_funding_schemes": [
            {
                "name": "MSME Innovative Scheme (Incubation, Design, IPR)",
                "organization": "Ministry of Micro, Small and Medium Enterprises (MSME)",
                "funding_type": "Grant-in-aid (Incubation Grant)",
                "funding_amount": "Up to ₹15 Lakhs per approved idea",
                "startup_stage": "Ideation / Prototype Validation",
                "deadline": "Ongoing",  # Unverified -> Should be marked STATUS: UNVERIFIED
                "eligibility": "Registered MSME unit holding valid Udyam Registration.",
                "who_can_apply": "Innovators and early software startups developing indigenous algorithmic tools.",
                "permitted_fund_usage": "Cloud sandbox infrastructure, security auditing, and design patents.",
                "why_suitable": "Provides early-stage prototyping support without equity dilution.",
                "where_to_apply": "MSME Innovative Official Portal (innovative.msme.gov.in)",
                "application_website": "https://innovative.msme.gov.in",
                "official_source_name": "Ministry of MSME Government of India",
                "official_source_url": "https://innovative.msme.gov.in",
                "application_steps": ["Obtain Udyam Registration.", "Submit application on innovative.msme.gov.in."],
                "required_documents": ["Udyam Registration Certificate", "Fintech Architecture Whitepaper"]
            },
            {
                "name": "MeitY SAMRIDH Accelerator Scheme",
                "organization": "Ministry of Electronics and Information Technology (MeitY Startup Hub)",
                "funding_type": "Matching Equity / Accelerator Investment",
                "funding_amount": "Up to ₹40 Lakhs matching capital",
                "startup_stage": "MVP / Early Traction",
                "deadline": "Cohort-based application deadlines",
                "eligibility": "Tech startups with software solution having validated MVP.",
                "who_can_apply": "Fintech software founders looking for customer acquisition scale.",
                "permitted_fund_usage": "Security compliance, team hiring, and marketing pipeline.",
                "why_suitable": "Accelerates onboarding with leading national fintech incubators.",
                "where_to_apply": "MeitY Startup Hub Portal via empaneled cohorts",
                "application_website": "https://meitystartuphub.in",
                "official_source_name": "MeitY Startup Hub",
                "official_source_url": "https://meitystartuphub.in",
                "application_steps": ["Apply through active cohort calls on MeitY Startup Hub."],
                "required_documents": ["Incorporation Certificate", "Live Sandbox Access Link"]
            }
        ],
        "private_funding_opportunities": [
            {
                "name": "Google for Startups Cloud Program",
                "organization": "Google LLC",
                "funding_type": "Cloud Credits & Technical Advisory",
                "funding_amount": "Up to $200,000 in Google Cloud Credits",
                "startup_stage": "Pre-Seed to Series A",
                "deadline": "Rolling application intake",
                "eligibility": "Fintech startups founded within last 5 years.",
                "who_can_apply": "Founders leveraging BigQuery and Vertex AI for financial analytics.",
                "permitted_fund_usage": "Cloud SQL, BigQuery analytics, Firebase authentication.",
                "why_suitable": "Essential for processing encrypted transaction streams with zero downtime.",
                "where_to_apply": "Google Cloud for Startups Portal",
                "application_website": "https://cloud.google.com/startup",
                "official_source_name": "Google Cloud Program",
                "official_source_url": "https://cloud.google.com/startup",
                "application_steps": ["Submit application via cloud.google.com/startup."],
                "required_documents": ["Corporate Email Domain", "Company Registration Number"]
            }
        ],
        "recommended_team_structure": [
            {
                "role": "CEO / Co-Founder",
                "department": "Executive Leadership",
                "reports_to": "",
                "priority": "Essential",
                "experience_level": "7+ years in consumer Fintech or Digital Banking",
                "why_needed": "Drives strategic vision, financial institution tie-ups, and investor fundraising.",
                "responsibilities": "Fundraising, bank partnership agreements, brand growth.",
                "required_skills": ["Consumer Fintech", "Fundraising", "Product Growth"],
                "soft_skills": ["Inspiring Communication", "Resilience"]
            },
            {
                "role": "Chief Compliance & Risk Officer",
                "department": "Legal & Regulatory",
                "reports_to": "CEO / Co-Founder",
                "priority": "Essential",
                "experience_level": "8+ years in SEBI, RBI, and DPDP Act compliance",
                "why_needed": "Ensures strict compliance with RBI Account Aggregator guidelines and SEBI RIA norms.",
                "responsibilities": "Managing SEBI Registered Investment Advisor licensing, DPDP audit, data governance.",
                "required_skills": ["SEBI Regulations", "RBI AA Guidelines", "DPDP Act", "Audit Documentation"],
                "soft_skills": ["Analytical Rigor", "Integrity"]
            },
            {
                "role": "Chief Technology Officer (CTO)",
                "department": "Engineering & Security",
                "reports_to": "CEO / Co-Founder",
                "priority": "Essential",
                "experience_level": "6+ years Financial Data Security & Banking APIs",
                "why_needed": "Architects end-to-end encrypted banking pipelines, SOC2 certification, and AI financial models.",
                "responsibilities": "Securing customer financial data, low-latency API aggregation, backend infra.",
                "required_skills": ["SOC2 Compliance", "Banking APIs", "Python", "PostgreSQL", "Fintech Security"],
                "soft_skills": ["Engineering Rigor", "Crisis Management"]
            },
            {
                "role": "VP Growth & Community",
                "department": "Growth & Marketing",
                "reports_to": "CEO / Co-Founder",
                "priority": "Later (Scale Stage)",
                "experience_level": "5+ years Organic Fintech Customer Acquisition",
                "why_needed": "Scales viral personal finance calculators and user acquisition channels.",
                "responsibilities": "SEO, personal finance content community, customer retention metrics.",
                "required_skills": ["Fintech SEO", "Performance Marketing", "Funnel Optimization"],
                "soft_skills": ["Storytelling", "Data-driven Mindset"]
            }
        ],
        "team_hierarchy": [
            {"role": "CEO / Co-Founder", "reports_to": "", "department": "Executive Leadership", "priority": "Essential"},
            {"role": "Chief Compliance & Risk Officer", "reports_to": "CEO / Co-Founder", "department": "Legal & Regulatory", "priority": "Essential"},
            {"role": "Chief Technology Officer (CTO)", "reports_to": "CEO / Co-Founder", "department": "Engineering & Security", "priority": "Essential"},
            {"role": "VP Growth & Community", "reports_to": "CEO / Co-Founder", "department": "Growth & Marketing", "priority": "Later"}
        ],
        "lean_team_advice": "In Fintech, Regulatory Risk Leadership (Compliance Officer) is just as critical as Engineering (CTO). Prioritize SEBI sandbox filings before aggressive consumer ad spend.",
        "competitor_analysis": [
            {
                "name": "INDmoney",
                "product_service": "All-in-one financial dashboard tracking mutual funds, stocks, and credit cards.",
                "target_customers": "Retail wealth builders and modern retail investors.",
                "business_model": "Brokerage, premium subscription tiers, and financial product distribution.",
                "pricing": "Free base app; ₹999/yr advisory services.",
                "funding_raised": "$150M+ (backed by Tiger Global, Steadview)",
                "revenue": "Estimated ₹80 Cr+ ARR (FY24 filings)",
                "profit_loss": "Operational reinvestment in financial super-app acquisition",
                "source": "Venture Intelligence, MCA Filings",
                "strengths": ["Deep native account tracking", "Massive user footprint"],
                "weaknesses": ["App complexity clutter", "Aggressive cross-selling of credit products"]
            }
        ],
        "startup_vs_competitors": [
            {"competitor": "INDmoney", "differentiation": "FinWise operates strictly as an objective, unbiased AI fiduciary without pushing third-party high-commission loans or spam products."}
        ],
        "financial_analysis": {
            "initial_capital_expenditure": "₹20 Lakhs (Account Aggregator licensing integration, VAPT audit, cloud security setup)",
            "monthly_operating_burn": "₹3.8 Lakhs/month during closed alpha sandbox testing",
            "projected_break_even": "Month 14 upon reaching 15,000 paid subscribers (₹199/month)",
            "funding_requirement": "₹1.0 Cr Pre-Seed round for SEBI licensing, SOC2 Type II audit, and user onboarding"
        },
        "risk_analysis": [
            {"category": "Regulatory & Fiduciary Risk", "description": "SEBI tightening registered investment advisory norms for AI-driven portfolio recommendations.", "mitigation": "Design system as execution & research tool, partnering with registered SEBI RIAs for formal sign-off."},
            {"category": "Data Security & Trust", "description": "Breach or unauthorized leakage of consumer banking financial telemetry.", "mitigation": "Zero-knowledge encryption where customer financial telemetry is never stored in plain text."}
        ],
        "roadmap": [
            {
                "step_number": 1,
                "phase_name": "Account Aggregator Sandbox & Encryption Engine",
                "estimated_timeline": "Months 1 - 3",
                "description": "Integrate Sahamati AA sandbox and deploy bank-grade zero-knowledge encryption."
            },
            {
                "step_number": 2,
                "phase_name": "SOC2 Audit & Closed Alpha Beta Testing",
                "estimated_timeline": "Months 4 - 6",
                "description": "Complete external VAPT audit and test algorithmic cashflow engine with 500 alpha users."
            }
        ],
        "important_recommendations": [
            "Complete SOC2 Type II audit and RBI Account Aggregator protocol integration prior to open marketing.",
            "Maintain ongoing security logging and audit trail reviews.",  # Unrelated ongoing test
            "Review MSME Innovative portal for active call notifications rather than treating it as open."
        ],
        "professional_networks_and_links": [
            {"name": "INDmoney Official LinkedIn Page", "source_type": "Competitor Profile", "category": "Market Intelligence", "url": "https://www.linkedin.com/company/indmoney"},
            {"name": "Fintech Convergence Council (FCC)", "source_type": "Industry Body", "category": "Fintech Network", "url": "https://www.fintechcouncil.in"},
            {"name": "Sahamati Account Aggregator Collective", "source_type": "Technical Resource", "category": "Banking Protocol", "url": "https://sahamati.org.in"}
        ]
    }


# ============================================================================
# STARTUP FIXTURE 3: 5-LEVEL DEEP HIERARCHY TEST TEAM
# ============================================================================

def get_5_level_hierarchy_team():
    return [
        {"role": "CEO / Founder", "reports_to": "", "department": "Executive Leadership", "priority": "Essential"},
        {"role": "Chief Technology Officer (CTO)", "reports_to": "CEO / Founder", "department": "Engineering", "priority": "Essential"},
        {"role": "Director of AI Systems", "reports_to": "Chief Technology Officer (CTO)", "department": "AI Research", "priority": "Essential"},
        {"role": "Lead Computer Vision Engineer", "reports_to": "Director of AI Systems", "department": "Computer Vision", "priority": "Essential"},
        {"role": "Senior PyTorch Specialist", "reports_to": "Lead Computer Vision Engineer", "department": "Model Training", "priority": "Later"},
    ]


# ============================================================================
# STARTUP FIXTURE 4: RESILIENCE & EDGE-CASE FIXTURE (SPARSE DATA)
# ============================================================================

def get_sparse_agritech_startup_data():
    return {
        "startup_name": "AgriDrone Systems",
        "industry": "Agricultural Robotics & Autonomous Spraying",
        "stage": "Concept Ideation",
        "executive_summary": "Autonomous precision drone fleet for localized pesticide micro-spraying on smallholder paddy farms.",
        "government_funding_schemes": [],
        "private_funding_opportunities": [],
        "recommended_team_structure": [
            {"role": "CEO / Founder", "department": "Operations", "priority": "Essential"}
        ],
        "competitor_analysis": [],
        "roadmap": []
    }


# ============================================================================
# TEXT EXTRACTION UTILITY
# ============================================================================

def extract_text_from_pdf(pdf_path: str) -> str:
    """Multi-tiered robust text extractor for verifying PDF content."""
    text = ""

    # Strategy 1: pypdf
    try:
        import pypdf
        reader = pypdf.PdfReader(pdf_path)
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
        if len(text.strip()) > 100:
            return text
    except Exception:
        pass

    # Strategy 2: PyPDF2
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(pdf_path)
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
        if len(text.strip()) > 100:
            return text
    except Exception:
        pass

    # Strategy 3: pdfminer
    try:
        from pdfminer.high_level import extract_text
        t = extract_text(pdf_path)
        if len(t.strip()) > 100:
            return t
    except Exception:
        pass

    # Strategy 4: Raw PDF stream decompression fallback
    try:
        with open(pdf_path, "rb") as f:
            data = f.read()
        parts = []
        stream_matches = re.findall(b'stream[\r\n]+(.*?)[\r\n]+endstream', data, re.DOTALL)
        for s in stream_matches:
            try:
                decomp = zlib.decompress(s)
                found_strings = re.findall(rb'\(((?:[^()\\]|\\.)*)\)', decomp)
                for item in found_strings:
                    parts.append(item.decode('latin-1', errors='ignore'))
            except Exception:
                pass
        extracted = " ".join(parts)
        if len(extracted.strip()) > 100:
            return extracted
    except Exception:
        pass

    return text


# ============================================================================
# TEST SUITE RUNNER
# ============================================================================

def run_tests():
    print("=" * 75)
    print("STARTUP INTELLIGENCE REPORT PDF: COMPREHENSIVE VERIFICATION SUITE")
    print("=" * 75)

    output_dir = os.path.join(current_dir, "test_output")
    os.makedirs(output_dir, exist_ok=True)

    pdf_health_path = os.path.join(output_dir, "report_healthcare_ai.pdf")
    pdf_finance_path = os.path.join(output_dir, "report_personal_finance_ai.pdf")
    pdf_sparse_path = os.path.join(output_dir, "report_sparse_agritech.pdf")

    test_results = []

    def assert_check(description: str, condition: bool, failure_msg: str = ""):
        status = "[PASS]" if condition else "[FAIL]"
        test_results.append((description, condition))
        print(f"  {status} {description}")
        if not condition and failure_msg:
            print(f"         DETAIL: {failure_msg}")

    # 1. Test Unrelated "ongoing" Text Sanitization
    print("\n[1/6] Testing Text Sanitization Precision:")
    sample_unrelated_1 = "Maintain ongoing clinical trials and ensure ongoing hospital partner feedback is recorded."
    clean_unrelated_1 = sanitize_sisfs_and_msme_recommendation(sample_unrelated_1)
    assert_check(
        "Unrelated 'ongoing' in sentence 1 remains completely unchanged",
        clean_unrelated_1 == sample_unrelated_1,
        f"Altered text: {clean_unrelated_1}"
    )

    sample_unrelated_2 = "Conduct ongoing user interviews to refine the product onboarding funnel."
    clean_unrelated_2 = sanitize_sisfs_and_msme_recommendation(sample_unrelated_2)
    assert_check(
        "Unrelated 'ongoing' in sentence 2 remains completely unchanged",
        clean_unrelated_2 == sample_unrelated_2,
        f"Altered text: {clean_unrelated_2}"
    )

    sample_sisfs = "Apply for the Startup India Seed Fund Scheme (SISFS) as ongoing seed capital."
    clean_sisfs = sanitize_sisfs_and_msme_recommendation(sample_sisfs)
    assert_check(
        "SISFS application instruction is sanitized to advise monitoring / alternatives",
        "monitor official portal announcements" in clean_sisfs.lower() and "closed" in clean_sisfs.lower(),
        f"Result: {clean_sisfs}"
    )

    # 2. Test Funding Status Logic Precision
    print("\n[2/6] Testing Funding Status Verification Logic:")
    # A date alone must NOT cause an opportunity to be marked OPEN
    date_only_status = get_opportunity_status("Generic Technology Grant", "Deadline: 31 December 2026")
    assert_check(
        "Funding opportunity with date-only deadline resolves to UNVERIFIED (never OPEN)",
        date_only_status[0] == "STATUS: UNVERIFIED",
        f"Returned: {date_only_status[0]}"
    )

    unverified_generic = get_opportunity_status("State Incubation Fund", "Not specified")
    assert_check(
        "Generic unverified opportunity resolves to UNVERIFIED",
        unverified_generic[0] == "STATUS: UNVERIFIED",
        f"Returned: {unverified_generic[0]}"
    )

    sisfs_status = get_opportunity_status("Startup India Seed Fund Scheme", "Ongoing")
    assert_check(
        "SISFS resolves strictly to STATUS: CLOSED with verified 31 May 2026 deadline",
        sisfs_status[0] == "STATUS: CLOSED" and "31 May 2026" in sisfs_status[5],
        f"Returned: {sisfs_status[0]}, {sisfs_status[5]}"
    )

    msme_status = get_opportunity_status("MSME Innovative Scheme", "Ongoing")
    assert_check(
        "MSME scheme without confirmed open evidence resolves to UNVERIFIED",
        msme_status[0] == "STATUS: UNVERIFIED",
        f"Returned: {msme_status[0]}"
    )

    verified_open_status = get_opportunity_status(
        "Biotech Innovation Call",
        "31 December 2026",
        status_str="Verified Active Call",
        evidence_str="Official source confirmed open via portal notification"
    )
    assert_check(
        "Opportunity with verified official-source evidence resolves to STATUS: OPEN",
        verified_open_status[0] == "STATUS: OPEN",
        f"Returned: {verified_open_status[0]}"
    )

    # 3. Test Dynamic Hierarchy Diagram with 5 Levels
    print("\n[3/6] Testing 5-Level Deep Hierarchy Diagram:")
    team_5_levels = get_5_level_hierarchy_team()
    diag_5 = build_multi_level_hierarchy_diagram(team_5_levels, team_5_levels)
    assert_check(
        "5-level hierarchy generates valid ReportLab Drawing",
        diag_5 is not None and diag_5.width == 515 and diag_5.height >= 200,
        f"Dimensions: w={diag_5.width if diag_5 else None}, h={diag_5.height if diag_5 else None}"
    )

    # 4. Generate Reports for Healthcare AI and Personal Finance AI
    print("\n[4/6] Generating Healthcare AI and Finance AI Reports...")
    health_data = get_healthcare_startup_data()
    generate_startup_intelligence_pdf("MedAI Diagnostics - AI Automated Radiology Triage", health_data, pdf_health_path)
    size_health = os.path.getsize(pdf_health_path) / 1024
    print(f"  -> Generated Healthcare AI report ({size_health:.2f} KB)")
    text_health = extract_text_from_pdf(pdf_health_path)

    finance_data = get_personal_finance_startup_data()
    generate_startup_intelligence_pdf("FinWise AI - Intelligent Algorithmic Wealth Mentor", finance_data, pdf_finance_path)
    size_finance = os.path.getsize(pdf_finance_path) / 1024
    print(f"  -> Generated Finance AI report ({size_finance:.2f} KB)")
    text_finance = extract_text_from_pdf(pdf_finance_path)

    sparse_data = get_sparse_agritech_startup_data()
    generate_startup_intelligence_pdf("AgriDrone Systems - Precision Crop Spraying", sparse_data, pdf_sparse_path)
    size_sparse = os.path.getsize(pdf_sparse_path) / 1024
    print(f"  -> Generated Sparse report ({size_sparse:.2f} KB)")
    text_sparse = extract_text_from_pdf(pdf_sparse_path)

    # 5. Core Content Assertions
    print("\n[5/6] Verifying Startup-Specific Content Separation:")
    assert_check(
        "Both Healthcare and Finance PDFs created and valid size (>15 KB)",
        size_health > 15.0 and size_finance > 15.0
    )

    assert_check(
        "Healthcare report contains Healthcare-specific roles (CMO, Radiologist, Clinical Trials)",
        ("Chief Medical Officer" in text_health or "Radiologist" in text_health) and "Clinical Affairs" in text_health
    )

    assert_check(
        "Finance report contains Finance-specific roles (Compliance Officer, SEBI, Risk, Banking APIs)",
        ("Chief Compliance" in text_finance or "SEBI" in text_finance) and "Legal & Regulatory" in text_finance
    )

    assert_check(
        "Roadmaps are startup-specific (PACS & CDSCO for Healthcare vs. Account Aggregator & SOC2 for Finance)",
        ("PACS" in text_health or "CDSCO" in text_health) and ("Account Aggregator" in text_finance or "SOC2" in text_finance)
    )

    assert_check(
        "Competitors are genuinely domain-specific (Qure.ai for Healthcare vs. INDmoney for Finance)",
        ("Qure.ai" in text_health and "Qure.ai" not in text_finance) and
        ("INDmoney" in text_finance and "INDmoney" not in text_health)
    )

    sections_to_check = [
        "1. Executive Summary",
        "2. Startup Idea and Business Model",
        "3. Market and Competitor Analysis",
        "4. Funding and Government Schemes",
        "5. Company and Team Structure",
        "6. Financial Analysis",
        "7. Risk Analysis",
        "8. Startup-Specific Roadmap",
        "9. Recommendations and Next Actions",
        "10. Professional Networks and Useful Links"
    ]
    for sec in sections_to_check:
        assert_check(
            f"Section present in Healthcare report: '{sec}'",
            sec.lower() in text_health.lower()
        )
        assert_check(
            f"Section present in Finance report: '{sec}'",
            sec.lower() in text_finance.lower()
        )

    # 6. Additional Structure & Integrity Assertions
    print("\n[6/6] Verifying Diagram Scenarios and Sparse Fallbacks:")
    assert_check(
        "Sparse/minimal startup idea generated without crash (>10 KB)",
        size_sparse > 10.0 and "AgriDrone Systems" in text_sparse
    )

    assert_check(
        "Official LinkedIn Company Setup link is present in Section 10",
        "linkedin.com/company/setup/new" in text_health and "linkedin.com/company/setup/new" in text_finance
    )

    test_teams = [
        ([{"role": "Solo Founder", "reports_to": "", "department": "Executive"}], "Single Solo Founder"),
        ([
            {"role": "CEO", "reports_to": "", "department": "Leadership"},
            {"role": "CTO", "reports_to": "CEO", "department": "Tech"},
            {"role": "COO", "reports_to": "CEO", "department": "Ops"},
        ], "Flat 3-role Team"),
        ([
            {"role": "CEO", "reports_to": "", "department": "Leadership"},
            {"role": "CTO", "reports_to": "CEO", "department": "Tech"},
            {"role": "CMO", "reports_to": "CEO", "department": "Medical"},
            {"role": "VP Sales", "reports_to": "CEO", "department": "Growth"},
            {"role": "Head of Product", "reports_to": "CEO", "department": "Product"},
        ], "Flat 5-role Team (Two Rows)"),
        ([
            {"role": "CEO", "reports_to": "", "department": "Leadership"},
            {"role": "CTO", "reports_to": "CEO", "department": "Engineering"},
            {"role": "CMO", "reports_to": "CEO", "department": "Clinical"},
            {"role": "Lead ML Engineer", "reports_to": "CTO", "department": "Engineering"},
            {"role": "Clinical Trial Specialist", "reports_to": "CMO", "department": "Clinical"},
            {"role": "Regulatory Specialist", "reports_to": "CEO", "department": "Compliance"},
        ], "Multi-Level 3-Tier Team"),
    ]

    for team_data, label in test_teams:
        dw = build_multi_level_hierarchy_diagram(team_data, team_data)
        assert_check(
            f"Dynamic hierarchy generator valid for: {label}",
            dw is not None and dw.width == 515 and (60 <= dw.height <= 260)
        )

    # Summary
    print("\n" + "=" * 75)
    passed = sum(1 for _, cond in test_results if cond)
    total = len(test_results)
    print(f"TOTAL TESTS : {total}")
    print(f"PASSED      : {passed}")
    print(f"FAILED      : {total - passed}")
    print("=" * 75)

    if passed == total:
        print("\nALL DYNAMIC INTELLIGENCE VERIFICATION CHECKS PASSED [100%]\n")
        return 0
    else:
        print(f"\nTEST SUITE FAILED: {total - passed} check(s) did not pass.\n")
        return 1


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)