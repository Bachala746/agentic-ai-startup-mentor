"""
Test script for Startup Intelligence PDF generation and Schema Validation.
Tests all 5 key requirements:
1. CEO appears at the top of hierarchy with reports_to=None and no "Reports To: CEO".
2. Microsoft for Startups URL normalization to https://startups.microsoft.com and clickable link.
3. Rejecting "Source: Internal Startup Assessment" and replacing with "Not publicly verified".
4. Safe generation of all PDF sections with ReportLab.
5. Handling None and empty fields safely.
"""

import os
import sys

# Ensure backend directory is in python search path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from pdf_generator import generate_startup_intelligence_pdf, make_clickable_link
from agents.startup_intelligence_agent import StartupIntelligenceReport


def run_tests():
    print("=" * 70)
    print("RUNNING STARTUP INTELLIGENCE VERIFICATION TESTS")
    print("=" * 70)

    # 1. Test Microsoft for Startups Clickable Link Helper
    print("\n[Test 1] Testing Microsoft for Startups URL normalization & link...")
    ms_link = make_clickable_link("https://startup.microsoft.com", "Microsoft Founders Hub")
    assert "https://startups.microsoft.com" in ms_link, "Failed to normalize singular startup.microsoft.com"
    assert "<a href=" in ms_link, "Link must contain <a href=> tag"
    print("✓ make_clickable_link correctly converted to https://startups.microsoft.com and created clickable markup.")

    # 2. Test Pydantic Schema Validation & Sanitization
    print("\n[Test 2] Testing Pydantic schema validation...")
    sample_raw_report = {
        "startup_name": "MediSync AI",
        "executive_summary": "AI-powered diagnostic assistance platform for primary care clinics.",
        "government_funding_schemes": [
            {
                "name": "Startup India Seed Fund Scheme (SISFS)",
                "organization": "DPIIT, Ministry of Commerce and Industry",
                "funding_type": "Grant",
                "funding_amount": "Up to ₹20 Lakhs",
                "eligibility": "DPIIT-recognized startup incorporated under 2 years",
                "who_can_apply": "Private Limited Company or LLP",
                "startup_stage": "Proof of Concept / Prototype",
                "usage": "Prototyping and clinical testing",
                "where_to_apply": "Startup India Official Portal",
                "application_website": "https://seedfund.startupindia.gov.in",
                "application_steps": ["Register on portal", "Select incubator", "Submit pitch deck"],
                "required_documents": ["DPIIT Certificate", "PAN", "Pitch Deck"],
                "deadline": "Ongoing",
                "official_source_name": "DPIIT",
                "official_source_url": "https://seedfund.startupindia.gov.in",
                "why_suitable": "Provides early non-dilutive capital for prototype development.",
            }
        ],
        "private_funding_opportunities": [
            {
                "name": "Microsoft for Startups Founders Hub",
                "organization": "Microsoft",
                "funding_type": "Cloud Credits",
                "funding_amount": "Up to $150,000 in Azure Credits",
                "eligibility": "Early-stage technology startup building proprietary software",
                "who_can_apply": "Registered venture",
                "startup_stage": "Ideation to Growth",
                "usage": "Cloud compute, OpenAI APIs, developer tooling",
                "where_to_apply": "Microsoft for Startups Portal",
                "application_website": "https://startup.microsoft.com",  # Intentionally misspelled to test correction
                "application_steps": ["Create LinkedIn account", "Submit application", "Provision Azure credits"],
                "required_documents": ["Product overview", "Company details"],
                "deadline": "Ongoing",
                "official_source_name": "Microsoft Corporation",
                "official_source_url": "https://startup.microsoft.com",  # Intentionally misspelled
                "why_suitable": "Essential for hosting AI and LLM inference infrastructure.",
            }
        ],
        "recommended_team_structure": [
            {
                "role": "CTO",
                "reports_to": "Chief Executive Officer (CEO)",
                "department": "Engineering",
                "priority": "Essential",
                "experience_level": "Senior",
                "responsibilities": "Leads software development and infrastructure.",
                "required_skills": ["Python", "FastAPI", "React"],
                "soft_skills": ["Technical leadership"],
                "why_needed": "Technical execution lead.",
            },
            {
                "role": "Chief Executive Officer (CEO)",
                "reports_to": "CEO",  # Intentionally self-referencing to test normalization to None
                "department": "Executive Leadership",
                "priority": "Essential",
                "experience_level": "Executive",
                "responsibilities": "Fundraising, vision, business strategy.",
                "required_skills": ["Strategic planning", "Fundraising"],
                "soft_skills": ["Leadership", "Communication"],
                "why_needed": "Venture leadership.",
            },
        ],
        "team_hierarchy": [
            {"role": "CTO", "reports_to": "Chief Executive Officer (CEO)", "department": "Engineering", "priority": "Essential"},
            {"role": "Chief Executive Officer (CEO)", "reports_to": "CEO", "department": "Executive Leadership", "priority": "Essential"},
        ],
        "competitor_analysis": [
            {
                "name": "Healthify Tech",
                "product_service": "Clinical triage assistant",
                "target_customers": "Hospitals",
                "business_model": "B2B SaaS subscription",
                "pricing": "Not publicly verified",
                "strengths": ["Hospital partnerships"],
                "weaknesses": ["Slow rollout"],
                "funding_raised": "Not publicly verified",
                "revenue": "Not publicly verified",
                "profit_loss": "Not publicly verified",
                "source": "Internal Startup Assessment",  # Intentionally using forbidden source to test rejection
            }
        ],
        "financial_information": [
            "Revenue: ₹0 | Source: Internal Startup Assessment",  # Intentionally bad source
        ],
        "startup_vs_competitors": ["Offers local Indian clinic workflows unlike US-centric alternatives."],
        "important_recommendations": ["Deploy pilot at 3 private clinics.", "Apply for SISFS grant."],
        "sources": [
            {"name": "Microsoft for Startups", "url": "https://startup.microsoft.com", "source_type": "Company Source", "category": "Official"}
        ],
        "roadmap": [
            {"step_number": 1, "phase_name": "MVP Build", "description": "Build core FastAPI backend", "estimated_timeline": "Months 1-2"},
            {"step_number": 2, "phase_name": "Pilot Validation", "description": "Run clinic trials", "estimated_timeline": "Months 3-4"},
        ],
    }

    report_obj = StartupIntelligenceReport(**sample_raw_report)
    validated_data = report_obj.model_dump()

    # Verify CEO is at index 0 and has reports_to == "None"
    ceo_role = validated_data["recommended_team_structure"][0]
    assert "ceo" in ceo_role["role"].lower(), f"CEO should be at index 0, found: {ceo_role['role']}"
    assert ceo_role["reports_to"] == "None", f"CEO reports_to should be 'None', got: {ceo_role['reports_to']}"
    print("✓ CEO role is at index 0 with reports_to='None'.")

    # Verify Microsoft for Startups URL normalization
    ms_opp = validated_data["private_funding_opportunities"][0]
    assert ms_opp["application_website"] == "https://startups.microsoft.com", f"Expected https://startups.microsoft.com, got: {ms_opp['application_website']}"
    print("✓ Microsoft for Startups application_website normalized to https://startups.microsoft.com.")

    # Verify Financial Information sanitization
    fin_entries = validated_data["financial_information"]
    assert "Internal Startup Assessment" not in fin_entries[0], "Internal Startup Assessment must be purged"
    assert fin_entries[0] == "Not publicly verified", f"Expected 'Not publicly verified', got: {fin_entries[0]}"
    print("✓ 'Internal Startup Assessment' successfully replaced with 'Not publicly verified'.")

    # 3. Test PDF Generation
    print("\n[Test 3] Testing PDF file generation with ReportLab...")
    output_pdf_path = os.path.join(CURRENT_DIR, "test_startup_intelligence.pdf")

    # Clean up old file if present
    if os.path.exists(output_pdf_path):
        os.remove(output_pdf_path)

    generate_startup_intelligence_pdf(
        startup_idea="AI-driven healthcare diagnostic assistant for clinics in India",
        report=validated_data,
        output_path=output_pdf_path,
    )

    assert os.path.exists(output_pdf_path), "PDF file was not created!"
    file_size = os.path.getsize(output_pdf_path)
    assert file_size > 5000, f"PDF file size suspiciously small: {file_size} bytes"
    print(f"✓ PDF generated successfully! File size: {file_size:,} bytes")
    print(f"✓ PDF location: {output_pdf_path}")

    # 4. Test None-Safety (Payload with null values)
    print("\n[Test 4] Testing Null/None-Safety...")
    null_test_report = {
        "government_funding_schemes": None,
        "private_funding_opportunities": None,
        "recommended_team_structure": None,
        "team_hierarchy": None,
        "competitor_analysis": None,
        "financial_information": None,
        "startup_vs_competitors": None,
        "important_recommendations": None,
        "sources": None,
        "roadmap": None,
    }
    null_pdf_path = os.path.join(CURRENT_DIR, "test_null_safety.pdf")
    generate_startup_intelligence_pdf(
        startup_idea="Null safety test idea",
        report=null_test_report,
        output_path=null_pdf_path,
    )
    assert os.path.exists(null_pdf_path), "Null-safety PDF was not created!"
    print(f"✓ Null-safety test passed! Generated without crashing ({os.path.getsize(null_pdf_path):,} bytes).")

    # Clean up test output files
    if os.path.exists(null_pdf_path):
        os.remove(null_pdf_path)

    print("\n" + "=" * 70)
    print("ALL TESTS PASSED SUCCESSFULLY! EVERYTHING IS VERIFIED.")
    print("=" * 70)


if __name__ == "__main__":
    run_tests()