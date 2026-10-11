import re
import html
import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    KeepTogether,
    HRFlowable,
    Table,
    TableStyle,
    PageBreak,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.colors import HexColor
from reportlab.graphics.shapes import (
    Drawing,
    Rect,
    String,
    Line,
    Polygon,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily


# ============================================================================
# UNICODE FONT REGISTRATION (FIX FOR INDIAN RUPEE ₹ SYMBOL & SPECIAL CHARS)
# ============================================================================

def setup_unicode_fonts():
    """
    Safely locates and registers a local TrueType font supporting Unicode
    characters, specifically including the Indian Rupee symbol (₹).
    Searches standard Linux, Windows, macOS, and virtualenv font directories.
    Falls back gracefully to Helvetica if no compatible TTF font is accessible.
    """
    candidate_pairs = []

    # 1. Matplotlib bundled DejaVu fonts if installed in Python environment
    try:
        import matplotlib
        mpl_dir = os.path.join(os.path.dirname(matplotlib.__file__), "mpl-data", "fonts", "ttf")
        mpl_reg = os.path.join(mpl_dir, "DejaVuSans.ttf")
        mpl_bold = os.path.join(mpl_dir, "DejaVuSans-Bold.ttf")
        if os.path.isfile(mpl_reg):
            candidate_pairs.append((mpl_reg, mpl_bold if os.path.isfile(mpl_bold) else mpl_reg))
    except Exception:
        pass

    # 2. Linux common fonts (Debian, Ubuntu, CentOS, Alpine, Docker)
    candidate_pairs.extend([
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        ("/usr/share/fonts/dejavu/DejaVuSans.ttf", "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf"),
        ("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf", "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf"),
        ("/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf", "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"),
        ("/usr/share/fonts/noto/NotoSans-Regular.ttf", "/usr/share/fonts/noto/NotoSans-Bold.ttf"),
        ("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
        ("/usr/share/fonts/truetype/freefont/FreeSans.ttf", "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"),
        ("/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf", "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf"),
    ])

    # 3. Windows system fonts
    win_dir = os.environ.get("WINDIR", "C:\\Windows")
    win_fonts = os.path.join(win_dir, "Fonts")
    candidate_pairs.extend([
        (os.path.join(win_fonts, "arial.ttf"), os.path.join(win_fonts, "arialbd.ttf")),
        (os.path.join(win_fonts, "segoeui.ttf"), os.path.join(win_fonts, "segoeuib.ttf")),
        (os.path.join(win_fonts, "calibri.ttf"), os.path.join(win_fonts, "calibrib.ttf")),
        (os.path.join(win_fonts, "Nirmala.ttf"), os.path.join(win_fonts, "NirmalaB.ttf")),
        (os.path.join(win_fonts, "tahoma.ttf"), os.path.join(win_fonts, "tahomabd.ttf")),
    ])

    # 4. macOS system fonts
    candidate_pairs.extend([
        ("/Library/Fonts/Arial.ttf", "/Library/Fonts/Arial Bold.ttf"),
        ("/System/Library/Fonts/Supplemental/Arial.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
        ("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"),
    ])

    # 5. Search in additional user/system font directories
    search_dirs = [
        "/usr/share/fonts",
        "/usr/local/share/fonts",
        os.path.expanduser("~/.fonts"),
        os.path.expanduser("~/.local/share/fonts"),
    ]
    for sdir in search_dirs:
        if os.path.isdir(sdir):
            for root, _, files in os.walk(sdir):
                for f in files:
                    fl = f.lower()
                    if fl.endswith(".ttf") and any(k in fl for k in ["dejavu", "noto", "liberation", "freesans", "arial"]):
                        fp = os.path.join(root, f)
                        candidate_pairs.append((fp, fp))

    # Attempt registration with ReportLab
    for reg_path, bold_path in candidate_pairs:
        if os.path.isfile(reg_path):
            try:
                font_name = "CustomUnicodeFont"
                bold_font_name = "CustomUnicodeFont-Bold"
                pdfmetrics.registerFont(TTFont(font_name, reg_path))
                actual_bold = bold_path if os.path.isfile(bold_path) else reg_path
                pdfmetrics.registerFont(TTFont(bold_font_name, actual_bold))
                try:
                    registerFontFamily(
                        font_name,
                        normal=font_name,
                        bold=bold_font_name,
                        italic=font_name,
                        boldItalic=bold_font_name,
                    )
                except Exception:
                    pass
                return font_name, bold_font_name
            except Exception:
                continue

    # Fallback to standard core fonts if no local TTF is accessible
    return "Helvetica", "Helvetica-Bold"


FONT_REGULAR, FONT_BOLD = setup_unicode_fonts()


# ============================================================================
# HELPER UTILITIES
# ============================================================================

def safe_text(val, fallback: str = "Not available") -> str:
    """Escapes XML/HTML entities for ReportLab and provides clean fallbacks."""
    if val is None:
        return fallback
    text = str(val).strip()
    if not text or text.lower() in ["none", "null", "n/a", "undefined"]:
        return fallback
    return html.escape(text)


def make_clickable_link(url: str, label: str = None) -> str:
    """Creates a clickable blue underlined link flowable markup."""
    url_str = str(url or "").strip()
    url_str = re.sub(
        r"startup\.microsoft\.com",
        "startups.microsoft.com",
        url_str,
        flags=re.IGNORECASE
    )
    if not url_str or url_str.lower() in ["not available", "not verified", "none", "n/a", "null", "not publicly specified", ""]:
        return '<font color="#64748B">Not publicly specified</font>'

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
# DYNAMIC MULTI-LEVEL ORGANIZATIONAL HIERARCHY BUILDER (NO EMPLOYEE COUNTS)
# ============================================================================

def build_multi_level_hierarchy_diagram(team_hierarchy: list, team_structure: list) -> Drawing:
    """
    Constructs a true multi-level tree organizational chart from reports_to
    relationships. Shows Role Name, Department, and Priority without employee counts.
    """
    raw_nodes = []

    # 1. Harvest nodes from team_hierarchy
    if team_hierarchy and isinstance(team_hierarchy, list):
        for item in team_hierarchy:
            if isinstance(item, dict) and item.get("role"):
                raw_nodes.append({
                    "role": item.get("role", "").strip(),
                    "reports_to": item.get("reports_to", "").strip(),
                    "department": item.get("department", "").strip(),
                    "priority": item.get("priority", "Essential").strip(),
                })

    # Enrich or fallback using team_structure
    struct_map = {}
    if team_structure and isinstance(team_structure, list):
        for s in team_structure:
            if isinstance(s, dict) and s.get("role"):
                r_name = s.get("role", "").strip().lower()
                struct_map[r_name] = s

    if not raw_nodes and team_structure and isinstance(team_structure, list):
        for s in team_structure:
            if isinstance(s, dict) and s.get("role"):
                raw_nodes.append({
                    "role": s.get("role", "").strip(),
                    "reports_to": s.get("reports_to", "CEO").strip(),
                    "department": s.get("department", "").strip(),
                    "priority": s.get("priority", "Essential").strip(),
                })

    if not raw_nodes:
        raw_nodes = [{
            "role": "CEO / Founder",
            "reports_to": "",
            "department": "Executive",
            "priority": "Essential",
        }]

    # Backfill missing metadata from struct_map
    for n in raw_nodes:
        key = n["role"].lower()
        if key in struct_map:
            meta = struct_map[key]
            if not n.get("department"):
                n["department"] = meta.get("department", "").strip()
            if not n.get("priority"):
                n["priority"] = meta.get("priority", "Essential").strip()

    # 2. Clean CEO root reporting
    for n in raw_nodes:
        r_lower = n["role"].lower()
        if "ceo" in r_lower or "founder" in r_lower:
            rep_lower = n.get("reports_to", "").lower()
            if rep_lower in ["founder/ceo", "ceo", "founder", "founder / ceo", r_lower, "none", "null"]:
                n["reports_to"] = ""

    # 3. Build Tree Indices
    node_by_role = {}
    children_by_role = {}

    for n in raw_nodes:
        r_name = n["role"]
        node_by_role[r_name] = n
        if r_name not in children_by_role:
            children_by_role[r_name] = []

    for n in raw_nodes:
        parent = n.get("reports_to", "").strip()
        if parent and parent != n["role"]:
            matched_parent = None
            for p_cand in node_by_role:
                if p_cand.lower() == parent.lower():
                    matched_parent = p_cand
                    break
            if matched_parent:
                children_by_role.setdefault(matched_parent, []).append(n["role"])

    # Identify Root Node (Leader / CEO)
    root_role = None
    for n in raw_nodes:
        if not n.get("reports_to") or n.get("reports_to").lower() in ["none", "null", ""]:
            root_role = n["role"]
            break
    if not root_role:
        for n in raw_nodes:
            if "ceo" in n["role"].lower() or "founder" in n["role"].lower():
                root_role = n["role"]
                n["reports_to"] = ""
                break
    if not root_role:
        root_role = raw_nodes[0]["role"]
        raw_nodes[0]["reports_to"] = ""

    # 4. Depth-First Traversal
    ordered_nodes = []  # entries of: (node_dict, depth, parent_role)
    visited = set()

    def traverse(curr_role, depth, parent_name):
        if curr_role in visited:
            return
        visited.add(curr_role)
        node_obj = node_by_role.get(curr_role)
        if node_obj:
            ordered_nodes.append((node_obj, depth, parent_name))
            for child_r in children_by_role.get(curr_role, []):
                traverse(child_r, depth + 1, curr_role)

    traverse(root_role, 0, "")

    # Attach any disconnected nodes under root at depth 1
    for n in raw_nodes:
        if n["role"] not in visited:
            traverse(n["role"], 1, root_role)

    # 5. Dynamic Sizing
    total_nodes = len(ordered_nodes)

    if total_nodes <= 8:
        card_h = 32
        gap = 10
        f_title = 8.5
        f_meta = 7.0
    elif total_nodes <= 12:
        card_h = 28
        gap = 8
        f_title = 8.0
        f_meta = 6.8
    elif total_nodes <= 16:
        card_h = 26
        gap = 7
        f_title = 7.5
        f_meta = 6.5
    else:
        card_h = 24
        gap = 5
        f_title = 7.0
        f_meta = 6.2

    diagram_width = 515
    diagram_height = max(140, total_nodes * (card_h + gap) + 30)

    d = Drawing(diagram_width, diagram_height)

    # 6. Compute geometry coordinates for each node
    node_coords = {}

    for idx, (node_data, depth, parent_name) in enumerate(ordered_nodes):
        r_name = node_data["role"]
        y_pos = diagram_height - 24 - (idx + 1) * (card_h + gap) + gap
        indent = 22 * min(depth, 4)
        x_pos = 20 + indent
        box_w = diagram_width - x_pos - 12

        node_coords[r_name] = {
            "x": x_pos,
            "y": y_pos,
            "w": box_w,
            "h": card_h,
            "depth": depth,
            "parent": parent_name,
            "data": node_data,
        }

    # 7. Draw Tree Connector Lines
    parent_to_direct_children = {}
    for r_name, coord in node_coords.items():
        p_name = coord["parent"]
        if p_name and p_name in node_coords:
            parent_to_direct_children.setdefault(p_name, []).append(r_name)

    for p_name, ch_names in parent_to_direct_children.items():
        if not ch_names:
            continue
        p_coord = node_coords[p_name]
        p_bottom_y = p_coord["y"]
        spine_x = p_coord["x"] + 14

        last_ch_name = ch_names[-1]
        last_ch_coord = node_coords[last_ch_name]
        last_ch_center_y = last_ch_coord["y"] + (card_h / 2)

        d.add(Line(
            spine_x, p_bottom_y,
            spine_x, last_ch_center_y,
            strokeColor=HexColor("#94A3B8"),
            strokeWidth=1.2,
        ))

        for ch_name in ch_names:
            ch_coord = node_coords[ch_name]
            ch_mid_y = ch_coord["y"] + (card_h / 2)
            d.add(Line(
                spine_x, ch_mid_y,
                ch_coord["x"], ch_mid_y,
                strokeColor=HexColor("#94A3B8"),
                strokeWidth=1.2,
            ))

    # 8. Render Each Role Card (Role + Department + Priority Pill, NO employee count)
    for idx, (node_data, depth, parent_name) in enumerate(ordered_nodes):
        r_name = node_data["role"]
        coord = node_coords[r_name]
        x = coord["x"]
        y = coord["y"]
        w = coord["w"]
        h = coord["h"]

        priority = node_data.get("priority", "Essential")
        is_essential = "essential" in priority.lower()
        dept = node_data.get("department", "")

        if depth == 0:
            bg_color = HexColor("#1E293B")
            border_color = None
            title_color = HexColor("#FFFFFF")
            meta_color = HexColor("#93C5FD")
        elif depth == 1:
            bg_color = HexColor("#EFF6FF")
            border_color = HexColor("#93C5FD")
            title_color = HexColor("#1E3A8A")
            meta_color = HexColor("#475569")
        elif depth == 2:
            bg_color = HexColor("#F8FAFC")
            border_color = HexColor("#CBD5E1")
            title_color = HexColor("#0F172A")
            meta_color = HexColor("#64748B")
        else:
            bg_color = HexColor("#FFFFFF")
            border_color = HexColor("#E2E8F0")
            title_color = HexColor("#1E293B")
            meta_color = HexColor("#64748B")

        # Card Box
        d.add(Rect(x, y, w, h, rx=4, ry=4, fillColor=bg_color, strokeColor=border_color, strokeWidth=1))

        # Title (Role)
        role_label = truncate_text(r_name, 38)
        title_y = y + (h * 0.54)
        d.add(String(x + 10, title_y, role_label, fontName=FONT_BOLD, fontSize=f_title, fillColor=title_color))

        # Department line (NO employee count)
        dept_label = truncate_text(dept, 34) if dept else "General"
        meta_str = f"Dept: {dept_label}"
        meta_y = y + (h * 0.16)
        d.add(String(x + 10, meta_y, meta_str, fontName=FONT_REGULAR, fontSize=f_meta, fillColor=meta_color))

        # Priority Badge
        badge_w = 54
        badge_h = min(15, h - 8)
        badge_x = x + w - badge_w - 6
        badge_y = y + (h - badge_h) / 2

        if depth == 0:
            badge_bg = HexColor("#334155")
            badge_fg = HexColor("#93C5FD")
            badge_text = "Leader"
        elif is_essential:
            badge_bg = HexColor("#DCFCE7")
            badge_fg = HexColor("#166534")
            badge_text = "Essential"
        else:
            badge_bg = HexColor("#FEF3C7")
            badge_fg = HexColor("#92400E")
            badge_text = "Later"

        d.add(Rect(badge_x, badge_y, badge_w, badge_h, rx=3, ry=3, fillColor=badge_bg, strokeColor=None))
        d.add(String(badge_x + (badge_w / 2), badge_y + 3.5, badge_text, fontName=FONT_BOLD, fontSize=6.8, fillColor=badge_fg, textAnchor="middle"))

    return d


# Backward-compatible alias
build_team_hierarchy_diagram = build_multi_level_hierarchy_diagram


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
        phase_name = truncate_text(item.get("phase_name", f"Phase {step_num}"), 42)
        timeline = truncate_text(item.get("estimated_timeline", ""), 22)
        desc = truncate_text(item.get("description", ""), 75)

        card_dw = Drawing(510, 50)
        card_dw.add(Rect(15, 2, 480, 46, rx=6, ry=6, fillColor=HexColor("#F8FAFC"), strokeColor=HexColor("#CBD5E1"), strokeWidth=1))

        # Step Badge Pill
        card_dw.add(Rect(26, 13, 62, 24, rx=4, ry=4, fillColor=HexColor("#2563EB"), strokeColor=None))
        card_dw.add(String(57, 20, f"Step {step_num}", fontName=FONT_BOLD, fontSize=8.5, fillColor=HexColor("#FFFFFF"), textAnchor="middle"))

        # Phase Title
        card_dw.add(String(98, 26, phase_name, fontName=FONT_BOLD, fontSize=9.5, fillColor=HexColor("#0F172A")))

        # Timeline
        if timeline:
            card_dw.add(String(482, 26, timeline, fontName=FONT_BOLD, fontSize=8.5, fillColor=HexColor("#2563EB"), textAnchor="end"))

        # Description
        if desc:
            card_dw.add(String(98, 11, desc, fontName=FONT_REGULAR, fontSize=8, fillColor=HexColor("#475569")))

        flowables.append(card_dw)

        # Connecting downward arrow between steps
        if idx < total_steps - 1:
            arrow_dw = Drawing(510, 16)
            arrow_dw.add(Line(255, 16, 255, 5, strokeColor=HexColor("#2563EB"), strokeWidth=1.5))
            arrow_dw.add(Polygon([250, 5, 260, 5, 255, 0], fillColor=HexColor("#2563EB"), strokeColor=HexColor("#2563EB")))
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
    from the structured intelligence analysis without employee counts.
    """
    report = report or {}

    # -------------------------------------------------------------------------
    # STYLES CONFIGURATION
    # -------------------------------------------------------------------------
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName=FONT_BOLD,
        fontSize=20,
        leading=24,
        textColor=HexColor("#0F172A"),
        alignment=TA_LEFT,
        spaceAfter=3,
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName=FONT_BOLD,
        fontSize=9.5,
        leading=13,
        textColor=HexColor("#2563EB"),
        alignment=TA_LEFT,
        spaceAfter=10,
    )

    h1_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName=FONT_BOLD,
        fontSize=12.5,
        leading=16,
        textColor=HexColor("#1E3A8A"),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True,
    )

    h2_style = ParagraphStyle(
        "SubSectionHeading",
        parent=styles["Normal"],
        fontName=FONT_BOLD,
        fontSize=10.5,
        leading=14,
        textColor=HexColor("#1D4ED8"),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True,
    )

    item_title_style = ParagraphStyle(
        "ItemTitle",
        parent=styles["Normal"],
        fontName=FONT_BOLD,
        fontSize=10,
        leading=13.5,
        textColor=HexColor("#0F172A"),
        spaceAfter=3,
    )

    body_style = ParagraphStyle(
        "StandardBody",
        parent=styles["Normal"],
        fontName=FONT_REGULAR,
        fontSize=8.5,
        leading=12.5,
        textColor=HexColor("#1E293B"),
    )

    bullet_style = ParagraphStyle(
        "BulletItem",
        parent=styles["Normal"],
        fontName=FONT_REGULAR,
        fontSize=8.5,
        leading=12.5,
        textColor=HexColor("#1E293B"),
        leftIndent=12,
        spaceAfter=3,
    )

    card_label_style = ParagraphStyle(
        "CardLabel",
        parent=styles["Normal"],
        fontName=FONT_BOLD,
        fontSize=8.5,
        leading=12,
        textColor=HexColor("#334155"),
        spaceAfter=2,
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
    content_width = 523  # A4 width (595.27) - margins (72)

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

    startup_name_val = report.get("startup_name")
    display_idea_text = f"<b>Target Startup Idea:</b> {safe_text(startup_idea, 'Not specified')}"
    if startup_name_val and str(startup_name_val).strip() and str(startup_name_val).strip().lower() != "not specified":
        display_idea_text = f"<b>Startup Name:</b> {safe_text(startup_name_val)} &nbsp;&nbsp;|&nbsp;&nbsp; " + display_idea_text

    idea_table = Table(
        [[Paragraph(display_idea_text, body_style)]],
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
    # 2. FUNDING OPPORTUNITIES (GOVERNMENT & PRIVATE)
    # -------------------------------------------------------------------------
    story.append(Paragraph("2. Funding Opportunities", h1_style))

    gov_funding = report.get("government_funding_schemes", [])
    priv_funding = report.get("private_funding_opportunities", [])

    # Backward compatibility fallback if both fields are empty
    if not gov_funding and not priv_funding:
        fallback_funding = report.get("funding_opportunities", [])
        if fallback_funding:
            for item in fallback_funding:
                if not isinstance(item, dict):
                    continue
                ftype = str(item.get("funding_type", "")).lower()
                org = str(item.get("organization", "")).lower()
                source = str(item.get("official_source", "")).lower()
                name = str(item.get("name", "")).lower()
                combined = f"{ftype} {org} {source} {name}"

                gov_keywords = ["gov", "ministry", "dpiit", "birac", "meity", "msme", "sidbi", "dst", "startup india", "sisfs", "state"]
                if any(k in combined for k in gov_keywords):
                    gov_funding.append(item)
                else:
                    priv_funding.append(item)

    def render_funding_card(opp: dict, is_government: bool = True):
        name = safe_text(opp.get("name") or opp.get("scheme_name"), "Funding Opportunity")
        org = safe_text(opp.get("organization") or opp.get("implementing_agency"), "Official Implementing Agency" if is_government else "Organization / Program")
        funding_type = safe_text(opp.get("funding_type"), "Grant" if is_government else "Private Capital / Program")
        amount = safe_text(opp.get("funding_amount") or opp.get("amount"), "Not publicly verified")
        stage = safe_text(opp.get("startup_stage") or opp.get("stage"), "Early / Validation")
        deadline = safe_text(opp.get("deadline"), "Not publicly specified")
        eligibility = safe_text(opp.get("eligibility"))
        who_can_apply = safe_text(opp.get("who_can_apply"))
        usage = safe_text(opp.get("usage") or opp.get("permitted_fund_usage"))
        why_suitable = safe_text(opp.get("why_suitable"))
        where_to_apply = safe_text(opp.get("where_to_apply"))
        app_website = opp.get("application_website") or opp.get("website") or ""

        source_name = safe_text(opp.get("official_source_name") or opp.get("official_source"), org)
        source_url = opp.get("official_source_url") or opp.get("source_url") or ""

        card_elements = [
            Paragraph(f"<b>{name}</b>", item_title_style),
            Spacer(1, 2),
            Paragraph(f"<b>Organization:</b> {org} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Funding Type:</b> {funding_type}", body_style),
            Paragraph(f"<b>Funding Amount:</b> {amount} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Startup Stage:</b> {stage}", body_style),
            Paragraph(f"<b>Deadline / Timeline:</b> {deadline}", body_style),
            Spacer(1, 2),
            Paragraph(f"<b>Eligibility:</b> {eligibility}", body_style),
            Paragraph(f"<b>Who Can Apply:</b> {who_can_apply}", body_style),
            Paragraph(f"<b>Permitted Fund Usage:</b> {usage}", body_style),
            Paragraph(f"<b>Why Suitable:</b> {why_suitable}", body_style),
            Paragraph(f"<b>Where to Apply:</b> {where_to_apply}", body_style),
            Paragraph(f"<b>Application Website:</b> {make_clickable_link(app_website, app_website)}", body_style),
            Paragraph(f"<b>Official Source:</b> {source_name}", body_style),
        ]

        if source_url and str(source_url).strip():
            card_elements.append(Paragraph(f"<b>Official Source Link:</b> {make_clickable_link(source_url, source_url)}", body_style))

        return KeepTogether([make_card(card_elements), Spacer(1, 6)])

    # 2A. Government Funding Schemes
    story.append(Paragraph("A. Government Funding Schemes", h2_style))
    if not gov_funding:
        story.append(Paragraph("<i>No government funding schemes recorded for this sector.</i>", body_style))
    else:
        for opp in gov_funding:
            if isinstance(opp, dict):
                story.append(render_funding_card(opp, is_government=True))

    story.append(Spacer(1, 4))

    # 2B. Private Funding Opportunities
    story.append(Paragraph("B. Private Funding Opportunities", h2_style))
    if not priv_funding:
        story.append(Paragraph("<i>No private funding opportunities recorded for this sector.</i>", body_style))
    else:
        for opp in priv_funding:
            if isinstance(opp, dict):
                story.append(render_funding_card(opp, is_government=False))

    story.append(section_divider())

    # -------------------------------------------------------------------------
    # 3. WHERE TO APPLY
    # -------------------------------------------------------------------------
    story.append(Paragraph("3. Where to Apply", h1_style))
    gov_list = gov_funding if isinstance(gov_funding, list) else []
    priv_list = priv_funding if isinstance(priv_funding, list) else []
    all_funding_list = [o for o in (gov_list + priv_list) if isinstance(o, dict)]

    if not all_funding_list:
        story.append(Paragraph("<i>No application portals available.</i>", body_style))
    else:
        for opp in all_funding_list:
            name = safe_text(opp.get("name") or opp.get("scheme_name"), "Funding Opportunity")
            org = safe_text(opp.get("organization") or opp.get("implementing_agency"), "Not specified")
            portal = safe_text(opp.get("where_to_apply"))
            website = opp.get("application_website") or opp.get("website") or ""
            deadline = safe_text(opp.get("deadline"))

            card_elements = [
                Paragraph(f"<b>{name}</b> &nbsp;<font color='#64748B'>({org})</font>", item_title_style),
                Spacer(1, 2),
                Paragraph(f"<b>Where to Apply:</b> {portal}", body_style),
                Paragraph(f"<b>Application Website:</b> {make_clickable_link(website, website)}", body_style),
                Paragraph(f"<b>Deadline / Timeline:</b> {deadline}", body_style),
            ]
            story.append(KeepTogether([make_card(card_elements), Spacer(1, 6)]))

    story.append(section_divider())

    # -------------------------------------------------------------------------
    # 4. APPLICATION STEPS
    # -------------------------------------------------------------------------
    story.append(Paragraph("4. Application Steps", h1_style))
    if not all_funding_list:
        story.append(Paragraph("<i>No application procedures recorded.</i>", body_style))
    else:
        for opp in all_funding_list:
            name = safe_text(opp.get("name") or opp.get("scheme_name"), "Funding Program")
            steps = opp.get("application_steps", [])
            docs = opp.get("required_documents", [])

            card_elements = [Paragraph(f"<b>{name} - Procedure & Checklist</b>", item_title_style), Spacer(1, 3)]

            # Steps
            card_elements.append(Paragraph("<b>Step-by-Step Procedure:</b>", card_label_style))
            if steps and isinstance(steps, list):
                for idx, step in enumerate(steps, 1):
                    card_elements.append(Paragraph(f"<b>Step {idx}:</b> {safe_text(step)}", bullet_style))
            elif isinstance(steps, str) and steps.strip():
                card_elements.append(Paragraph(safe_text(steps), bullet_style))
            else:
                card_elements.append(Paragraph("Procedure details: Check official portal guidelines.", bullet_style))

            Spacer(1, 3)
            # Documents
            card_elements.append(Paragraph("<b>Required Documents:</b>", card_label_style))
            if docs and isinstance(docs, list):
                for doc_item in docs:
                    card_elements.append(Paragraph(f"• {safe_text(doc_item)}", bullet_style))
            elif isinstance(docs, str) and docs.strip():
                card_elements.append(Paragraph(safe_text(docs), bullet_style))
            else:
                card_elements.append(Paragraph("Document checklist: As specified on the official application portal.", bullet_style))

            story.append(KeepTogether([make_card(card_elements), Spacer(1, 6)]))

    story.append(section_divider())

    # -------------------------------------------------------------------------
    # 5. RECOMMENDED COMPANY / TEAM STRUCTURE (NO EMPLOYEE COUNTS)
    # -------------------------------------------------------------------------
    story.append(Paragraph("5. Recommended Company / Team Structure", h1_style))
    team_list = report.get("recommended_team_structure", [])

    if not team_list:
        story.append(Paragraph("<i>No team structure data available.</i>", body_style))
    else:
        essential_roles = [r for r in team_list if isinstance(r, dict) and "later" not in str(r.get("priority", "")).lower()]
        later_roles = [r for r in team_list if isinstance(r, dict) and "later" in str(r.get("priority", "")).lower()]

        def render_role_cards(role_group, group_label):
            if not role_group:
                return
            story.append(Paragraph(group_label, h2_style))
            for role_item in role_group:
                role_title = safe_text(role_item.get("role"), "Role Title")
                dept = safe_text(role_item.get("department"), "General")
                reports_to = (
                    "Not applicable (Top-level leader)"
                    if "ceo" in str(role_item.get("role", "")).lower()
                    or "founder" in str(role_item.get("role", "")).lower()
                    else safe_text(role_item.get("reports_to"), "CEO")
                )
                priority = safe_text(role_item.get("priority"), "Essential")
                exp_level = safe_text(role_item.get("experience_level"), "Not specified")
                why_needed = safe_text(role_item.get("why_needed"))
                responsibilities = safe_text(role_item.get("responsibilities"))

                skills = role_item.get("required_skills") or role_item.get("skills") or []
                if isinstance(skills, list):
                    skills_text = ", ".join([safe_text(s) for s in skills]) if skills else "Not specified"
                else:
                    skills_text = safe_text(skills)

                soft_skills = role_item.get("soft_skills") or []
                if isinstance(soft_skills, list):
                    soft_skills_text = ", ".join([safe_text(s) for s in soft_skills]) if soft_skills else ""
                else:
                    soft_skills_text = safe_text(soft_skills)

                card_elements = [
                    Paragraph(f"<b>{role_title}</b> &nbsp;<font color='#2563EB'>({priority})</font>", item_title_style),
                    Spacer(1, 2),
                    Paragraph(f"<b>Department:</b> {dept} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Reports To:</b> {reports_to} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Experience Level:</b> {exp_level}", body_style),
                    Spacer(1, 2),
                    Paragraph(f"<b>Why Needed:</b> {why_needed}", body_style),
                    Paragraph(f"<b>Key Responsibilities:</b> {responsibilities}", body_style),
                    Paragraph(f"<b>Required Skills:</b> {skills_text}", body_style),
                ]

                if soft_skills_text:
                    card_elements.append(Paragraph(f"<b>Soft Skills:</b> {soft_skills_text}", body_style))

                story.append(KeepTogether([make_card(card_elements), Spacer(1, 5)]))

        render_role_cards(essential_roles, "Essential Roles (Immediate / MVP Stage)")
        render_role_cards(later_roles, "Roles That Can Be Added Later (Scale / Expansion Stage)")

    # 5B. Multi-Level Organizational Tree Diagram (NO employee counts)
    hierarchy_nodes = report.get("team_hierarchy", [])
    total_nodes_for_diag = len(hierarchy_nodes or []) if hierarchy_nodes else len(team_list or [])

    if total_nodes_for_diag > 8:
        story.append(PageBreak())
    else:
        story.append(Spacer(1, 8))

    story.append(Paragraph("Dynamic Multi-Level Team Hierarchy", h2_style))
    story.append(Paragraph("<i>Organizational reporting structure mapped from CEO down through department heads, leads, and specialists:</i>", body_style))
    story.append(Spacer(1, 6))

    hierarchy_diagram = build_multi_level_hierarchy_diagram(
        hierarchy_nodes,
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
            funding_raised = safe_text(comp.get("funding_raised") or comp.get("funding"), "Not publicly verified")
            revenue = safe_text(comp.get("revenue"), "Not publicly verified")
            profit_loss = safe_text(comp.get("profit_loss"), "Not publicly verified")
            c_source = safe_text(comp.get("source"), "Public intelligence / market records")
            strengths = comp.get("strengths", [])
            weaknesses = comp.get("weaknesses", [])

            card_elements = [
                Paragraph(f"<b>{c_name}</b>", item_title_style),
                Spacer(1, 2),
                Paragraph(f"<b>Product / Service:</b> {p_s}", body_style),
                Paragraph(f"<b>Target Customers:</b> {target}", body_style),
                Paragraph(f"<b>Business Model:</b> {model} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Pricing:</b> {pricing}", body_style),
                Paragraph(f"<b>Funding Raised:</b> {funding_raised}", body_style),
                Paragraph(f"<b>Verified Revenue:</b> {revenue} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Verified Profit/Loss:</b> {profit_loss}", body_style),
                Paragraph(f"<b>Data Source:</b> {c_source}", body_style),
            ]

            if strengths:
                s_text = ", ".join([safe_text(s) for s in strengths]) if isinstance(strengths, list) else safe_text(strengths)
                card_elements.append(Paragraph(f"<b>Strengths:</b> {s_text}", body_style))
            if weaknesses:
                w_text = ", ".join([safe_text(w) for w in weaknesses]) if isinstance(weaknesses, list) else safe_text(weaknesses)
                card_elements.append(Paragraph(f"<b>Weaknesses / Gaps:</b> {w_text}", body_style))

            story.append(KeepTogether([make_card(card_elements), Spacer(1, 6)]))

    story.append(section_divider())

    # -------------------------------------------------------------------------
    # 7. FINANCIAL INFORMATION
    # -------------------------------------------------------------------------
    story.append(Paragraph("7. Financial Information", h1_style))
    fin_info = report.get("financial_information", [])

    if not fin_info:
        story.append(Paragraph("<i>Financial Information: Not publicly verified.</i>", body_style))
    else:
        fin_elements = []
        if isinstance(fin_info, list):
            for item in fin_info:
                if isinstance(item, dict):
                    rev = safe_text(item.get("revenue"), "Not verified")
                    pl = safe_text(item.get("profit_loss"), "Not verified")
                    funding = safe_text(item.get("funding_raised"), "Not verified")
                    src = safe_text(item.get("source"), "Public filing")
                    fin_elements.append(Paragraph(f"• <b>Revenue:</b> {rev} | <b>Profit/Loss:</b> {pl} | <b>Funding Raised:</b> {funding} (Source: {src})", bullet_style))
                else:
                    fin_elements.append(Paragraph(f"• {safe_text(item)}", bullet_style))
        elif isinstance(fin_info, dict):
            for k, v in fin_info.items():
                fin_elements.append(Paragraph(f"• <b>{safe_text(k).replace('_', ' ').title()}:</b> {safe_text(v)}", bullet_style))
        else:
            fin_elements.append(Paragraph(f"• {safe_text(fin_info)}", bullet_style))

        story.append(make_card(fin_elements))

    story.append(section_divider())

    # -------------------------------------------------------------------------
    # 8. STARTUP VS COMPETITORS
    # -------------------------------------------------------------------------
    story.append(Paragraph("8. Startup vs Competitors", h1_style))
    comparison = report.get("startup_vs_competitors", [])

    if not comparison:
        story.append(Paragraph("<i>Comparison breakdown not available.</i>", body_style))
    else:
        comp_elements = []
        if isinstance(comparison, list):
            for point in comparison:
                if isinstance(point, dict):
                    c_target = safe_text(point.get("competitor") or point.get("name"), "Competitor")
                    diff = safe_text(point.get("differentiation") or point.get("comparison"), "")
                    comp_elements.append(Paragraph(f"• <b>vs {c_target}:</b> {diff}", bullet_style))
                else:
                    comp_elements.append(Paragraph(f"• {safe_text(point)}", bullet_style))
        elif isinstance(comparison, dict):
            for k, v in comparison.items():
                comp_elements.append(Paragraph(f"• <b>{safe_text(k)}:</b> {safe_text(v)}", bullet_style))
        else:
            comp_elements.append(Paragraph(f"• {safe_text(comparison)}", bullet_style))

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
        if isinstance(recommendations, list):
            for idx, rec in enumerate(recommendations, 1):
                rec_elements.append(Paragraph(f"<b>{idx}.</b> {safe_text(rec)}", bullet_style))
        else:
            rec_elements.append(Paragraph(safe_text(recommendations), bullet_style))
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
                src_name = safe_text(src.get("name") or src.get("title"), "Official Source")
                src_type = safe_text(src.get("source_type") or src.get("type"), "")
                src_cat = safe_text(src.get("category"), "")
                src_url = src.get("url") or ""

                meta_line = []
                if src_type and src_type.lower() not in ["not available", "none"]:
                    meta_line.append(f"<b>Type:</b> {src_type}")
                if src_cat and src_cat.lower() not in ["not available", "none"]:
                    meta_line.append(f"<b>Category:</b> {src_cat}")

                meta_str = f" &nbsp;|&nbsp; {' &nbsp;|&nbsp; '.join(meta_line)}" if meta_line else ""
                source_elements.append(Paragraph(f"• <b>{src_name}</b>{meta_str}", bullet_style))
                source_elements.append(Paragraph(f"&nbsp;&nbsp;<b>Link:</b> {make_clickable_link(src_url, src_url)}", bullet_style))
            elif isinstance(src, str):
                source_elements.append(Paragraph(f"• <b>Source Link:</b> {make_clickable_link(src, src)}", bullet_style))

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
        # 11A. Detailed Roadmap Phases
        for idx, r_step in enumerate(roadmap_list, 1):
            if not isinstance(r_step, dict):
                continue
            s_num = safe_text(r_step.get("step_number", idx))
            s_phase = safe_text(r_step.get("phase_name", f"Phase {s_num}"))
            s_time = safe_text(r_step.get("estimated_timeline"))
            s_desc = safe_text(r_step.get("description"))

            card_elements = [
                Paragraph(f"<b>Phase {s_num}: {s_phase}</b> &nbsp;<font color='#2563EB'>({s_time})</font>", item_title_style),
                Spacer(1, 2),
                Paragraph(s_desc, body_style),
            ]
            story.append(KeepTogether([make_card(card_elements), Spacer(1, 4)]))

        # 11B. Dynamic Roadmap Vector Diagram
        story.append(Spacer(1, 6))
        story.append(Paragraph("<b>Startup Execution Flowchart:</b>", card_label_style))
        story.append(Spacer(1, 4))
        diagram_flowables = build_roadmap_diagram(roadmap_list)
        story.append(KeepTogether(diagram_flowables))

    # -------------------------------------------------------------------------
    # BUILD PDF
    # -------------------------------------------------------------------------
    doc.build(story)