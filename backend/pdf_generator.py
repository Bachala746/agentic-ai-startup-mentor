from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER


def generate_startup_intelligence_pdf(
    startup_idea: str,
    report: dict,
    output_path: str,
):
    styles = getSampleStyleSheet()
    title = styles["Title"]
    title.alignment = TA_CENTER

    story = [
        Paragraph("Startup Intelligence Report", title),
        Spacer(1, 15),
        Paragraph(f"<b>Startup Idea:</b> {startup_idea}", styles["Normal"]),
        Spacer(1, 15),
    ]

    def add_heading(text):
        story.append(Paragraph(f"<b>{text}</b>", styles["Heading2"]))
        story.append(Spacer(1, 8))

    def add_text(text):
        story.append(Paragraph(str(text), styles["Normal"]))
        story.append(Spacer(1, 6))

    add_heading("Executive Summary")
    add_text(report.get("executive_summary", "Not available"))

    add_heading("Funding & Government Schemes")
    for item in report.get("funding_opportunities", []):
        add_text(f"<b>{item.get('name', '')}</b>")
        add_text(f"Type: {item.get('funding_type', '')}")
        add_text(f"Amount: {item.get('funding_amount', '')}")
        add_text(f"Eligibility: {item.get('eligibility', '')}")
        add_text(f"Where to Apply: {item.get('where_to_apply', '')}")
        add_text(f"Website: {item.get('application_website', '')}")
        add_text(f"Steps: {', '.join(item.get('application_steps', []))}")

    add_heading("Recommended Company / Team Structure")
    for role in report.get("recommended_team_structure", []):
        add_text(f"<b>{role.get('role', '')}</b>")
        add_text(role.get("responsibilities", ""))
        add_text(f"Skills: {', '.join(role.get('skills', []))}")
        add_text(f"Priority: {role.get('priority', '')}")

    add_heading("Competitor Analysis")
    for competitor in report.get("competitor_analysis", []):
        add_text(f"<b>{competitor.get('name', '')}</b>")
        add_text(f"Product/Service: {competitor.get('product_service', '')}")
        add_text(f"Customers: {competitor.get('target_customers', '')}")
        add_text(f"Business Model: {competitor.get('business_model', '')}")
        add_text(f"Pricing: {competitor.get('pricing', '')}")
        add_text(f"Revenue: {competitor.get('revenue', '')}")
        add_text(f"Profit/Loss: {competitor.get('profit_loss', '')}")

    add_heading("Financial Information")
    for item in report.get("financial_information", []):
        add_text(item)

    add_heading("Important Recommendations")
    for item in report.get("important_recommendations", []):
        add_text(f"• {item}")

    add_heading("Sources / Official Links")
    for source in report.get("sources", []):
        add_text(source)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    doc.build(story)