import html
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    KeepTogether,
    HRFlowable,
    Table,
    TableStyle,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.colors import HexColor
from reportlab.graphics.shapes import (
    Drawing,
    Rect,
    String,
    Line,
    Polygon,
    Group,
)


# ============================================================================
# HELPER UTILITIES
# ============================================================================

def safe_text(val, fallback: str = "Not available") -> str:
    """Escapes XML/HTML entities for ReportLab and provides clean fallbacks."""
    if val is None:
        return fallback
    text = str(val).strip()
    if not text or text.lower() in ["none", "null", "n/a", ""]:
        return fallback
    return html.escape(text)


def make_clickable_link(url: str, label: str = None) -> str:
    """Creates a clickable blue underlined link flowable markup."""
    url_str = str(url or "").strip()
    if not url_str or url_str.lower() in ["not available", "not verified", "none", ""]:
        return '<font color="#64748B">Not verified</font>'
    
    href = url_str if url_str.startswith(("http://", "https://")) else f"https://{url_str}"
    display_label = label if label else url_str
    
    safe_href = html.escape(href, quote=True)
    safe_label = html.escape(display_label)
    return f'<font color="#1D4ED8"><u><a href="{safe_href}">{safe_label}</a></u></font>'


def truncate_text(text: str, max_chars: int = 40) -> str:
    """Truncates string for diagram labels to prevent graphical overflow."""
    text = str(text or "").strip()
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3] + "..."


# ============================================================================
# DYNAMIC DIAGRAM BUILDERS
# ============================================================================

def build_team_hierarchy_diagram(team_hierarchy: list, team_structure: list) -> Drawing:
    """
    Renders a dynamic organizational tree diagram using vector drawing components.
    Adapts dynamically to the startup's team roles and reporting relationships.
    """
    # Extract nodes
    nodes = []
    if team_hierarchy and isinstance(team_hierarchy, list):
        for item in team_hierarchy:
            if isinstance(item, dict) and item.get("role"):
                nodes.append({
                    "role": item.get("role", "").strip(),
                    "reports_to": item.get("reports_to", "").strip(),
                    "priority": "Essential",
                })

    # Fallback to team_structure if team_hierarchy is missing or empty
    if not nodes and team_structure and isinstance(team_structure, list):
        for item in team_structure:
            if isinstance(item, dict) and item.get("role"):
                nodes.append({
                    "role": item.get("role", "").strip(),
                    "reports_to": item.get("reports_to", "Founder/CEO").strip(),
                    "priority": item.get("priority", "Essential").strip(),
                })

    # Always ensure root node exists
    has_root = any(not n["reports_to"] or "founder" in n["role"].lower() or "ceo" in n["role"].lower() for n in nodes)
    if not has_root:
        nodes.insert(0, {"role": "Founder / CEO", "reports_to": "", "priority": "Essential"})

    # Limit to maximum 8 nodes for clean single-page presentation
    nodes = nodes[:8]
    total_nodes = len(nodes)
    card_height = 26
    row_gap = 14
    diagram_height = max(140, total_nodes * (card_height + row_gap) + 20)
    diagram_width = 500

    d = Drawing(diagram_width, diagram_height)
    spine_x = 45

    # Identify root node
    root_idx = 0
    for idx, n in enumerate(nodes):
        if not n["reports_to"] or "founder" in n["role"].lower() or "ceo" in n["role"].lower():
            root_idx = idx
            break
    root_node = nodes.pop(root_idx)
    ordered_nodes = [root_node] + nodes

    # Calculate y-positions (ReportLab Y=0 is at bottom)
    current_y = diagram_height - 35

    # 1. Draw Root Box (Founder/CEO)
    root_role = truncate_text(ordered_nodes[0]["role"], 36)
    d.add(Rect(20, current_y, 230, 28, rx=5, ry=5, fillColor=HexColor("#1E293B"), strokeColor=None))
    d.add(String(30, current_y + 9, root_role, fontName="Helvetica-Bold", fontSize=9.5, fillColor=HexColor("#FFFFFF")))
    
    # Priority pill for root
    d.add(Rect(185, current_y + 5, 55, 17, rx=3, ry=3, fillColor=HexColor("#334155"), strokeColor=None))
    d.add(String(212, current_y + 10, "Leader", fontName="Helvetica-Bold", fontSize=7.5, fillColor=HexColor("#93C5FD"), textAnchor="middle"))

    last_branch_y = current_y

    # 2. Draw Branching Child Nodes
    for i in range(1, len(ordered_nodes)):
        node = ordered_nodes[i]
        role_title = truncate_text(node.get("role", "Team Member"), 38)
        priority = node.get("priority", "Essential")
        is_essential = "essential" in priority.lower()

        current_y -= (card_height + row_gap)
        last_branch_y = current_y + 13

        # Horizontal branch connector from spine
        d.add(Line(spine_x, current_y + 13, spine_x + 30, current_y + 13, strokeColor=HexColor("#94A3B8"), strokeWidth=1.5))

        # Child Role Card
        box_x = spine_x + 30
        box_w = 400
        d.add(Rect(box_x, current_y, box_w, card_height, rx=4, ry=4, fillColor=HexColor("#F8FAFC"), strokeColor=HexColor("#CBD5E1"), strokeWidth=1))
        d.add(String(box_x + 10, current_y + 8, role_title, fontName="Helvetica-Bold", fontSize=8.5, fillColor=HexColor("#0F172A")))

        # Priority Badge
        badge_w = 60
        badge_x = box_x + box_w - badge_w - 8
        badge_bg = HexColor("#DCFCE7") if is_essential else HexColor("#FEF3C7")
        badge_fg = HexColor("#166534") if is_essential else HexColor("#92400E")
        badge_label = "Essential" if is_essential else "Later"

        d.add(Rect(badge_x, current_y + 4, badge_w, 17, rx=3, ry=3, fillColor=badge_bg, strokeColor=None))
        d.add(String(badge_x + (badge_w / 2), current_y + 9, badge_label, fontName="Helvetica-Bold", fontSize=7.5, fillColor=badge_fg, textAnchor="middle"))

    # 3. Draw Vertical Trunk Line from Root to Last Branch
    if len(ordered_nodes) > 1:
        d.add(Line(spine_x, diagram_height - 35, spine_x, last_branch_y, strokeColor=HexColor("#94A3B8"), strokeWidth=1.5))

    return d


def build_roadmap_diagram(roadmap_items: list) -> list:
    """
    Constructs a sequential flowchart diagram representing the startup roadmap.
    Generates dynamic phase cards linked by directional arrows.
    """
    flowables = []
    if not roadmap_items or not isinstance(roadmap_items, list):
        return [Paragraph("<i>No roadmap flow available.</i>", getSampleStyleSheet()["Normal"])]

    steps = [s for s in roadmap_items if isinstance(s, dict)]
    total_steps = len(steps)

    for idx, item in enumerate(steps):
        step_num = item.get("step_number", idx + 1)
        phase_name = truncate_text(item.get("phase_name", f"Phase {step_num}"), 36)
        timeline = truncate_text(item.get("estimated_timeline", ""), 20)
        desc = truncate_text(item.get("description", ""), 65)

        card_dw = Drawing(500, 48)
        # Background card
        card_dw.add(Rect(15, 2, 470, 44, rx=6, ry=6, fillColor=HexColor("#F8FAFC"), strokeColor=HexColor("#CBD5E1"), strokeWidth=1))

        # Phase Badge Pill
        card_dw.add(Rect(26, 12, 60, 22, rx=4, ry=4, fillColor=HexColor("#2563EB"), strokeColor=None))
        card_dw.add(String(56, 18, f"Step {step_num}", fontName="Helvetica-Bold", fontSize=8.5, fillColor=HexColor("#FFFFFF"), textAnchor="middle"))

        # Phase Title
        card_dw.add(String(96, 24, phase_name, fontName="Helvetica-Bold", fontSize=10, fillColor=HexColor("#0F172A")))

        # Timeline (Right aligned)
        if timeline:
            card_dw.add(String(472, 24, timeline, fontName="Helvetica-Bold", fontSize=8.5, fillColor=HexColor("#2563EB"), textAnchor="end"))

        # Description line
        if desc:
            card_dw.add(String(96, 10, desc, fontName="Helvetica", fontSize=8, fillColor=HexColor("#475569")))

        flowables.append(card_dw)

        # Draw connecting downward arrow if not last step
        if idx < total_steps - 1:
            arrow_dw = Drawing(500, 18)
            # Arrow trunk
            arrow_dw.add(Line(250, 18, 250, 6, strokeColor=HexColor("#2563EB"), strokeWidth=1.5))
            # Downward arrowhead
            arrow_dw.add(Polygon([245, 6, 255, 6, 250, 0], fillColor=HexColor("#2563EB"), strokeColor=HexColor("#2563EB")))
            flowables.append(arrow_dw)

    return flowables


# ============================================================================
# MAIN PDF GENERATION FUNCTION
# ============================================================================

def generate_startup_intelligence_pdf(
    startup_idea: str,
    report: dict,
    output_path: str,
):
    """
    Generates a professional executive-ready Startup Intelligence Report PDF
    from the structured intelligence analysis.
    """
    report = report or {}

    # -------------------------------------------------------------------------
    # STYLES CONFIGURATION
    # -------------------------------------------------------------------------
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=HexColor("#0F172A"),
        alignment=TA_LEFT,
        spaceAfter=3,
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=13,
        textColor=HexColor("#2563EB"),
        alignment=TA_LEFT,
        spaceAfter=10,
    )

    h1_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12.5,
        leading=16,
        textColor=HexColor("#1E3A8A"),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True,
    )

    item_title_style = ParagraphStyle(
        "ItemTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=14,
        textColor=HexColor("#0F172A"),
        spaceAfter=3,
    )

    body_style = ParagraphStyle(
        "StandardBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12.5,
        textColor=HexColor("#1E293B"),
    )

    bullet_style = ParagraphStyle(
        "BulletItem",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12.5,
        textColor=HexColor("#1E293B"),
        leftIndent=12,
        spaceAfter=3,
    )

    card_label_style = ParagraphStyle(
        "CardLabel",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=12,
        textColor=HexColor("#334155"),
    )

    # -------------------------------------------------------------------------
    # DOCUMENT SETUP
    # -------------------------------------------------------------------------
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    story = []
    content_width = 523  # A4 width (595) - margins (72)

    def section_divider():
        return HRFlowable(
            width="100%",
            thickness=0.5,
            color=HexColor("#E2E8F0"),
            spaceBefore=8,
            spaceAfter=8,
        )

    def make_card(flowables_list) -> Table:
        card_table = Table([[flowables_list]], colWidths=[content_width])
        card_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), HexColor("#F8FAFC")),
            ("BOX", (0, 0), (-1, -1), 0.5, HexColor("#CBD5E1")),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        return card_table

    # -------------------------------------------------------------------------
    # COVER / HEADER BLOCK
    # -------------------------------------------------------------------------
    story.append(Paragraph("Startup Intelligence Report", title_style))
    story.append(Paragraph("AGENTIC AI PERSONALIZED STARTUP MENTOR", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=HexColor("#2563EB"), spaceBefore=0, spaceAfter=8))

    idea_table = Table(
        [[Paragraph(f"<b>Target Startup Idea:</b> {safe_text(startup_idea, 'Not specified')}", body_style)]],
        colWidths=[content_width],
    )
    idea_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), HexColor("#EFF6FF")),
        ("BOX", (0, 0), (-1, -1), 0.5, HexColor("#93C5FD")),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(idea_table)
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------------------
    # 1. EXECUTIVE SUMMARY
    # -------------------------------------------------------------------------
    story.append(Paragraph("1. Executive Summary", h1_style))
    exec_summary = safe_text(report.get("executive_summary"), "Executive summary not available.")
    story.append(Paragraph(exec_summary, body_style))
    story.append(section_divider())

    # -------------------------------------------------------------------------
    # 2. FUNDING & GOVERNMENT SCHEMES
    # -------------------------------------------------------------------------
    story.append(Paragraph("2. Funding & Government Schemes", h1_style))
    funding_list = report.get("funding_opportunities", [])

    if not funding_list:
        story.append(Paragraph("<i>No verified funding schemes recorded.</i>", body_style))
    else:
        for opp in funding_list:
            if not isinstance(opp, dict):
                continue

            card_elements = [
                Paragraph(f"<b>{safe_text(opp.get('name'), 'Scheme Name')}</b>", item_title_style),
                Spacer(1, 3),
                Paragraph(f"<b>Funding Type:</b> {safe_text(opp.get('funding_type'))} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Funding Amount:</b> {safe_text(opp.get('funding_amount'))}", body_style),
                Paragraph(f"<b>Startup Stage:</b> {safe_text(opp.get('startup_stage'))} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Deadline:</b> {safe_text(opp.get('deadline'))}", body_style),
                Spacer(1, 2),
                Paragraph(f"<b>Eligibility:</b> {safe_text(opp.get('eligibility'))}", body_style),
                Paragraph(f"<b>Who Can Apply:</b> {safe_text(opp.get('who_can_apply'))}", body_style),
                Paragraph(f"<b>Permitted Fund Usage:</b> {safe_text(opp.get('usage'))}", body_style),
                Paragraph(f"<b>Why Suitable:</b> {safe_text(opp.get('why_suitable'))}", body_style),
                Paragraph(f"<b>Official Source:</b> {safe_text(opp.get('official_source'))}", body_style),
            ]
            story.append(KeepTogether([make_card(card_elements), Spacer(1, 6)]))

    story.append(section_divider())

    # -------------------------------------------------------------------------
    # 3. WHERE TO APPLY
    # -------------------------------------------------------------------------
    story.append(Paragraph("3. Where to Apply", h1_style))
    if not funding_list:
        story.append(Paragraph("<i>No application portals available.</i>", body_style))
    else:
        for opp in funding_list:
            if not isinstance(opp, dict):
                continue

            name = safe_text(opp.get("name"), "Funding Program")
            portal = safe_text(opp.get("where_to_apply"))
            website = opp.get("application_website", "")
            deadline = safe_text(opp.get("deadline"))

            card_elements = [
                Paragraph(f"<b>{name}</b>", item_title_style),
                Spacer(1, 2),
                Paragraph(f"<b>Application Portal / Authority:</b> {portal}", body_style),
                Paragraph(f"<b>Official Website:</b> {make_clickable_link(website, website)}", body_style),
                Paragraph(f"<b>Deadline / Timeline:</b> {deadline}", body_style),
            ]
            story.append(KeepTogether([make_card(card_elements), Spacer(1, 6)]))

    story.append(section_divider())

    # -------------------------------------------------------------------------
    # 4. APPLICATION STEPS
    # -------------------------------------------------------------------------
    story.append(Paragraph("4. Application Steps", h1_style))
    if not funding_list:
        story.append(Paragraph("<i>No application procedures recorded.</i>", body_style))
    else:
        for opp in funding_list:
            if not isinstance(opp, dict):
                continue

            name = safe_text(opp.get("name"), "Funding Program")
            steps = opp.get("application_steps", [])
            docs = opp.get("required_documents", [])

            card_elements = [Paragraph(f"<b>{name} - Procedure & Checklist</b>", item_title_style), Spacer(1, 3)]

            # Steps
            card_elements.append(Paragraph("<b>Step-by-Step Procedure:</b>", card_label_style))
            if steps:
                for idx, step in enumerate(steps, 1):
                    card_elements.append(Paragraph(f"{idx}. {safe_text(step)}", bullet_style))
            else:
                card_elements.append(Paragraph("Procedure details: Not verified", bullet_style))

            Spacer(1, 3)
            # Required Docs
            card_elements.append(Paragraph("<b>Required Documents:</b>", card_label_style))
            if docs:
                for doc_item in docs:
                    card_elements.append(Paragraph(f"• {safe_text(doc_item)}", bullet_style))
            else:
                card_elements.append(Paragraph("Document checklist: Not verified", bullet_style))

            story.append(KeepTogether([make_card(card_elements), Spacer(1, 6)]))

    story.append(section_divider())

    # -------------------------------------------------------------------------
    # 5. RECOMMENDED COMPANY / TEAM STRUCTURE
    # -------------------------------------------------------------------------
    story.append(Paragraph("5. Recommended Company / Team Structure", h1_style))
    team_list = report.get("recommended_team_structure", [])

    if not team_list:
        story.append(Paragraph("<i>No team structure data available.</i>", body_style))
    else:
        for role_item in team_list:
            if not isinstance(role_item, dict):
                continue

            role_title = safe_text(role_item.get("role"), "Role Title")
            priority = safe_text(role_item.get("priority"), "Essential")
            reports_to = safe_text(role_item.get("reports_to"), "Founder/CEO")
            why_needed = safe_text(role_item.get("why_needed"))
            responsibilities = safe_text(role_item.get("responsibilities"))
            skills = role_item.get("skills", [])
            skills_text = ", ".join([safe_text(s) for s in skills]) if skills else "Not specified"

            card_elements = [
                Paragraph(f"<b>{role_title}</b> &nbsp;<font color='#2563EB'>({priority})</font>", item_title_style),
                Spacer(1, 2),
                Paragraph(f"<b>Reports To:</b> {reports_to}", body_style),
                Paragraph(f"<b>Why Needed:</b> {why_needed}", body_style),
                Paragraph(f"<b>Responsibilities:</b> {responsibilities}", body_style),
                Paragraph(f"<b>Key Skills:</b> {skills_text}", body_style),
            ]
            story.append(KeepTogether([make_card(card_elements), Spacer(1, 6)]))

    # Team Hierarchy Vector Diagram
    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>Dynamic Team Reporting Hierarchy:</b>", card_label_style))
    story.append(Spacer(1, 4))
    hierarchy_diagram = build_team_hierarchy_diagram(
        report.get("team_hierarchy", []),
        team_list,
    )
    story.append(KeepTogether([hierarchy_diagram, Spacer(1, 6)]))

    story.append(section_divider())

    # -------------------------------------------------------------------------
    # 6. COMPETITOR ANALYSIS
    # -------------------------------------------------------------------------
    story.append(Paragraph("6. Competitor Analysis", h1_style))
    competitors = report.get("competitor_analysis", [])

    if not competitors:
        story.append(Paragraph("<i>No competitor information recorded.</i>", body_style))
    else:
        for comp in competitors:
            if not isinstance(comp, dict):
                continue

            c_name = safe_text(comp.get("name"), "Competitor")
            p_s = safe_text(comp.get("product_service"))
            target = safe_text(comp.get("target_customers"))
            model = safe_text(comp.get("business_model"))
            pricing = safe_text(comp.get("pricing"))
            revenue = safe_text(comp.get("revenue"), "Not publicly verified")
            profit_loss = safe_text(comp.get("profit_loss"), "Not publicly verified")
            c_source = safe_text(comp.get("source"), "Public intelligence")
            strengths = comp.get("strengths", [])
            weaknesses = comp.get("weaknesses", [])

            card_elements = [
                Paragraph(f"<b>{c_name}</b>", item_title_style),
                Spacer(1, 2),
                Paragraph(f"<b>Product / Service:</b> {p_s}", body_style),
                Paragraph(f"<b>Target Customers:</b> {target}", body_style),
                Paragraph(f"<b>Business Model:</b> {model} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Pricing:</b> {pricing}", body_style),
                Paragraph(f"<b>Verified Revenue:</b> {revenue}", body_style),
                Paragraph(f"<b>Verified Profit/Loss:</b> {profit_loss}", body_style),
                Paragraph(f"<b>Data Source:</b> {c_source}", body_style),
            ]

            if strengths:
                card_elements.append(Paragraph(f"<b>Strengths:</b> {', '.join([safe_text(s) for s in strengths])}", body_style))
            if weaknesses:
                card_elements.append(Paragraph(f"<b>Weaknesses / Gaps:</b> {', '.join([safe_text(w) for w in weaknesses])}", body_style))

            story.append(KeepTogether([make_card(card_elements), Spacer(1, 6)]))

    story.append(section_divider())

    # -------------------------------------------------------------------------
    # 7. FINANCIAL INFORMATION
    # -------------------------------------------------------------------------
    story.append(Paragraph("7. Financial Information", h1_style))
    fin_info = report.get("financial_information", [])

    if not fin_info:
        story.append(Paragraph("<i>Not publicly verified.</i>", body_style))
    else:
        fin_elements = []
        for item in fin_info:
            fin_elements.append(Paragraph(f"• {safe_text(item)}", bullet_style))
        story.append(make_card(fin_elements))

    story.append(section_divider())

    # -------------------------------------------------------------------------
    # 8. STARTUP VS COMPETITORS
    # -------------------------------------------------------------------------
    story.append(Paragraph("8. Startup vs Competitors", h1_style))
    comparison = report.get("startup_vs_competitors", [])

    if not comparison:
        story.append(Paragraph("<i>Comparison points not available.</i>", body_style))
    else:
        comp_elements = []
        for point in comparison:
            comp_elements.append(Paragraph(f"• {safe_text(point)}", bullet_style))
        story.append(make_card(comp_elements))

    story.append(section_divider())

    # -------------------------------------------------------------------------
    # 9. IMPORTANT RECOMMENDATIONS
    # -------------------------------------------------------------------------
    story.append(Paragraph("9. Important Recommendations", h1_style))
    recommendations = report.get("important_recommendations", [])

    if not recommendations:
        story.append(Paragraph("<i>Recommendations not available.</i>", body_style))
    else:
        rec_elements = []
        for idx, rec in enumerate(recommendations, 1):
            rec_elements.append(Paragraph(f"<b>{idx}.</b> {safe_text(rec)}", bullet_style))
        story.append(make_card(rec_elements))

    story.append(section_divider())

    # -------------------------------------------------------------------------
    # 10. SOURCES / OFFICIAL LINKS
    # -------------------------------------------------------------------------
    story.append(Paragraph("10. Sources / Official Links", h1_style))
    sources_list = report.get("sources", [])

    if not sources_list:
        story.append(Paragraph("<i>No verified external sources recorded.</i>", body_style))
    else:
        source_elements = []
        for src in sources_list:
            if isinstance(src, dict):
                src_name = safe_text(src.get("name"), "Official Portal")
                src_url = src.get("url", "")
                link_html = make_clickable_link(src_url, src_url)
                source_elements.append(Paragraph(f"• <b>{src_name}:</b> {link_html}", bullet_style))
            elif isinstance(src, str):
                link_html = make_clickable_link(src, src)
                source_elements.append(Paragraph(f"• {link_html}", bullet_style))
        story.append(make_card(source_elements))

    story.append(section_divider())

    # -------------------------------------------------------------------------
    # 11. STARTUP ROADMAP & FLOWCHART DIAGRAM
    # -------------------------------------------------------------------------
    story.append(Paragraph("11. Startup Roadmap", h1_style))
    roadmap_list = report.get("roadmap", [])

    if not roadmap_list:
        story.append(Paragraph("<i>Roadmap details not available.</i>", body_style))
    else:
        # 11A. Detailed Roadmap Phases Table
        for r_step in roadmap_list:
            if not isinstance(r_step, dict):
                continue
            s_num = safe_text(r_step.get("step_number"))
            s_phase = safe_text(r_step.get("phase_name"))
            s_time = safe_text(r_step.get("estimated_timeline"))
            s_desc = safe_text(r_step.get("description"))

            card_elements = [
                Paragraph(f"<b>Phase {s_num}: {s_phase}</b> &nbsp;<font color='#2563EB'>({s_time})</font>", item_title_style),
                Spacer(1, 2),
                Paragraph(s_desc, body_style),
            ]
            story.append(KeepTogether([make_card(card_elements), Spacer(1, 4)]))

        # 11B. Dynamic Roadmap Vector Diagram at the End
        story.append(Spacer(1, 8))
        story.append(Paragraph("<b>Startup Execution Flowchart:</b>", card_label_style))
        story.append(Spacer(1, 6))
        diagram_flowables = build_roadmap_diagram(roadmap_list)
        story.append(KeepTogether(diagram_flowables))

    # -------------------------------------------------------------------------
    # BUILD PDF
    # -------------------------------------------------------------------------
    doc.build(story)