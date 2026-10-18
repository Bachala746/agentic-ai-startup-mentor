import re
import html
import os
from datetime import datetime
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
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.lib.colors import HexColor
from reportlab.graphics.shapes import (
    Drawing,
    Rect,
    String,
    Line,
    Polygon,
)
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily


# ============================================================================
# UNICODE FONT REGISTRATION (INDIAN RUPEE â‚¹ SYMBOL & SPECIAL CHARS)
# ============================================================================

def setup_unicode_fonts():
    """
    Safely locates and registers a local TrueType font supporting Unicode
    characters, specifically including the Indian Rupee symbol (â‚¹).
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
    candidate_extend_mac = [
        ("/Library/Fonts/Arial.ttf", "/Library/Fonts/Arial Bold.ttf"),
        ("/System/Library/Fonts/Supplemental/Arial.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
        ("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"),
    ]
    candidate_pairs.extend(candidate_extend_mac)

    # 5. Additional user/system font directories
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

    return "Helvetica", "Helvetica-Bold"


FONT_REGULAR, FONT_BOLD = setup_unicode_fonts()


# ============================================================================
# NUMBERED CANVAS (RUNNING HEADER & "PAGE X OF Y" FOOTER)
# ============================================================================

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas that dynamically calculates the total page count
    and renders professional running headers and footers on each page.
    """
    startup_name = "Startup Intelligence Report"
    generated_date = datetime.now().strftime("%B %d, %Y")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()

        # Running Header (pages > 1)
        if self._pageNumber > 1:
            self.setFont(FONT_REGULAR, 7.5)
            self.setFillColor(HexColor("#64748B"))
            header_text = f"Startup Intelligence Report | {self.startup_name}"
            if len(header_text) > 65:
                header_text = header_text[:62] + "..."
            self.drawString(36, 810, header_text)
            self.drawRightString(559, 810, "CONFIDENTIAL & PROPRIETARY")
            self.setStrokeColor(HexColor("#E2E8F0"))
            self.setLineWidth(0.6)
            self.line(36, 804, 559, 804)

        # Running Footer (all pages)
        self.setStrokeColor(HexColor("#E2E8F0"))
        self.setLineWidth(0.6)
        self.line(36, 28, 559, 28)

        self.setFont(FONT_REGULAR, 7.5)
        self.setFillColor(HexColor("#64748B"))
        self.drawString(36, 18, f"Agentic AI Startup Mentor â€¢ Prepared {self.generated_date} â€¢ Verified & Dynamic Intelligence")
        self.drawRightString(559, 18, f"Page {self._pageNumber} of {page_count}")

        self.restoreState()


# ============================================================================
# HELPER UTILITIES
# ============================================================================

def safe_text(val, fallback: str = "Not publicly specified") -> str:
    """Escapes XML/HTML entities for ReportLab and provides clean fallbacks."""
    if val is None:
        return fallback
    text = str(val).strip()
    if not text or text.lower() in ["none", "null", "n/a", "undefined"]:
        return fallback
    return html.escape(text)


def make_clickable_link(url: str, label: str = None) -> str:
    """Creates a validated, clickable blue underlined link markup for ReportLab."""
    url_str = str(url or "").strip()
    if not url_str or url_str.lower() in [
        "not available",
        "not verified",
        "none",
        "n/a",
        "null",
        "not publicly specified",
        "",
    ]:
        return '<font color="#64748B">Not publicly specified</font>'

    # Normalize known provider URL domains
    url_str = re.sub(r"startup\.microsoft\.com", "startups.microsoft.com", url_str, flags=re.IGNORECASE)
    url_str = re.sub(r"^http://", "https://", url_str, flags=re.IGNORECASE)

    href = url_str if url_str.startswith("https://") else f"https://{url_str}"
    display_label = label if label else url_str
    display_label = re.sub(r"startup\.microsoft\.com", "startups.microsoft.com", str(display_label), flags=re.IGNORECASE)

    # Truncate extremely long visual URLs to prevent overflow
    if len(display_label) > 65 and "/" in display_label:
        parts = display_label.split("/")
        display_label = f"{parts[0]}//{parts[2]}/.../{parts[-1]}" if len(parts) >= 4 else display_label[:62] + "..."

    safe_href = html.escape(href, quote=True)
    safe_label = html.escape(display_label)
    return f'<font color="#1D4ED8"><u><a href="{safe_href}">{safe_label}</a></u></font>'


def truncate_text(text: str, max_chars: int = 40) -> str:
    """Truncates string for diagram labels to prevent graphical overflow."""
    text = str(text or "").strip()
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3] + "..."


def sanitize_sisfs_and_msme_recommendation(text: str) -> str:
    """
    Sanitizes SISFS and MSME mentions so neither is presented as open.
    Targets ONLY specific SISFS and MSME phrases without altering unrelated
    occurrences of the word 'ongoing' elsewhere in the text.
    """
    if not text or not isinstance(text, str):
        return "" if text is None else str(text)

    t = text

    # 1. Action instructing applying / leveraging SISFS as an open scheme
    sisfs_action_pattern = re.compile(
        r'(?i)(?:apply\s+(?:for|to)|submit\s+(?:an?\s+)?application\s+(?:for|to)|seek\s+(?:funding\s+from)?|leverage|utilize|target|tap\s+into|consider\s+applying\s+to|explore\s+applying\s+to)\s+(?:the\s+)?(?:startup\s+india\s+seed\s+fund(?:\s+scheme)?|sisfs)[^.;\n]*',
        re.IGNORECASE
    )
    if sisfs_action_pattern.search(t):
        replacement = (
            "Monitor official portal announcements (seedfund.startupindia.gov.in) for successor schemes to the Startup India Seed Fund Scheme "
            "(SISFS, closed for new applications on 31 May 2026) or explore currently eligible alternatives (such as BIRAC BIG and cloud accelerator grants)"
        )
        t = sisfs_action_pattern.sub(replacement, t)

    # 2. Status / ongoing label attached directly to SISFS
    t = re.sub(
        r'(?i)\b(sisfs|startup india seed fund(?:\s+scheme)?)\s*(?:\((?:ongoing|open)\)|[-:â€“]\s*(?:ongoing|open)|\s+is\s+(?:ongoing|open))\b',
        r'\1 (Closed on 31 May 2026; monitor official portal for successor calls or explore active alternatives)',
        t
    )
    t = re.sub(
        r'(?i)\b(?:ongoing|open)\s+(sisfs|startup india seed fund(?:\s+scheme)?)\b',
        r'\1 (Closed on 31 May 2026; monitor official portal for successor calls or explore active alternatives)',
        t
    )

    # 3. Status / ongoing label attached directly to MSME
    t = re.sub(
        r'(?i)\b(msme(?:\s+innovative(?:\s+scheme)?)?)\s*(?:\((?:ongoing|open)\)|[-:â€“]\s*(?:ongoing|open)|\s+is\s+(?:ongoing|open))\b',
        r'\1 (Status Unverified â€” Check Official Portal)',
        t
    )
    t = re.sub(
        r'(?i)\b(?:ongoing|open)\s+(msme(?:\s+innovative(?:\s+scheme)?)?)\b',
        r'\1 (Status Unverified â€” Check Official Portal)',
        t
    )

    return t


def get_opportunity_status(
    opp_name: str,
    deadline_str: str,
    status_str: str = "",
    evidence_str: str = ""
) -> tuple[str, str, str, str, str, str]:
    """
    Returns (status_label, badge_bg, badge_fg, border_color, card_bg, normalized_deadline).
    Guarantees:
    - Never marks unverified opportunities as open based only on names, dates, or keywords.
    - SISFS is strictly labeled CLOSED with deadline 31 May 2026.
    - Marks OPEN only when current, reliable official-source evidence confirms applications are open.
    - If status cannot be verified, displays 'STATUS: UNVERIFIED'.
    """
    name_lower = str(opp_name or "").lower()
    dl_lower = str(deadline_str or "").lower()
    st_lower = str(status_str or "").lower()
    ev_lower = str(evidence_str or "").lower()
    combined_ctx = f"{dl_lower} {st_lower} {ev_lower}"

    # 1. Startup India Seed Fund Scheme (SISFS) - Application Window Closed
    if "sisfs" in name_lower or "startup india seed fund" in name_lower:
        status_label = "STATUS: CLOSED"
        badge_bg = "#FEE2E2"
        badge_fg = "#991B1B"
        border_color = "#FCA5A5"
        card_bg = "#FFF9F9"
        normalized_deadline = (
            "Closed on 31 May 2026 (Applications closed for new startups; "
            "incubator selection concluded 30 June 2026)"
        )
        return status_label, badge_bg, badge_fg, border_color, card_bg, normalized_deadline

    # 2. Explicit Closed / Expired
    if any(k in dl_lower for k in ["closed", "ended", "expired"]) or any(k in st_lower for k in ["closed", "ended", "expired"]):
        return (
            "STATUS: CLOSED",
            "#FEE2E2",
            "#991B1B",
            "#FCA5A5",
            "#FFF9F9",
            deadline_str or "Applications closed",
        )

    # 3. Check for Reliable Official-Source Evidence Confirming Applications are Open
    has_confirmed_evidence = (
        any(k in combined_ctx for k in [
            "official source confirmed open",
            "confirmed open by official portal",
            "verified active application window",
            "active call verified open",
            "officially confirmed open",
            "active call open through",
        ])
        and not any(k in combined_ctx for k in ["unverified", "closed", "ended", "expired"])
    )
    if has_confirmed_evidence:
        return (
            "STATUS: OPEN",
            "#DCFCE7",
            "#166534",
            "#BBF7D0",
            "#F8FAFC",
            deadline_str or "Applications open (Officially verified)",
        )

    # 4. Strict Fallback: Display UNVERIFIED (Never mark OPEN without reliable official confirmation)
    return (
        "STATUS: UNVERIFIED",
        "#FEF3C7",
        "#92400E",
        "#FCD34D",
        "#FFFDF7",
        deadline_str if (deadline_str and deadline_str.strip() and dl_lower not in ["none", "null", "n/a", "undefined", "not publicly specified"]) else "Status unverified â€” Check official portal for active call announcements",
    )


# ============================================================================
# COMPACT DYNAMIC ORGANIZATIONAL HIERARCHY BUILDER (ALL DEPTHS)
# ============================================================================

def build_multi_level_hierarchy_diagram(team_hierarchy: list, team_structure: list) -> Drawing:
    """
    Constructs a clean, professional, compact organizational hierarchy chart.
    Places the CEO at the top, department roles beneath, and connects roles using
    clear reporting bus lines and downward-pointing arrows.
    Dynamically renders EVERY reporting level (including 5+ levels) without missing
    roles, overlapping cards, or crossed reporting lines.
    """
    raw_nodes = []

    if team_hierarchy and isinstance(team_hierarchy, list):
        for item in team_hierarchy:
            if isinstance(item, dict) and item.get("role"):
                raw_nodes.append({
                    "role": item.get("role", "").strip(),
                    "reports_to": item.get("reports_to", "").strip(),
                    "department": item.get("department", "").strip(),
                    "priority": item.get("priority", "Essential").strip(),
                })

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
            "department": "Executive Leadership",
            "priority": "Essential",
        }]

    # Merge metadata
    for n in raw_nodes:
        key = n["role"].lower()
        if key in struct_map:
            meta = struct_map[key]
            if not n.get("department"):
                n["department"] = meta.get("department", "").strip()
            if not n.get("priority"):
                n["priority"] = meta.get("priority", "Essential").strip()

    # Normalize Root (CEO / Founder)
    for n in raw_nodes:
        r_lower = n["role"].lower()
        if "ceo" in r_lower or "founder" in r_lower:
            rep_lower = n.get("reports_to", "").lower()
            if rep_lower in ["founder/ceo", "ceo", "founder", "founder / ceo", r_lower, "none", "null", ""]:
                n["reports_to"] = ""
        elif n.get("reports_to", "").strip().lower() == r_lower:
            n["reports_to"] = ""

    node_by_role = {}
    children_by_role = {}
    for n in raw_nodes:
        r_name = n["role"]
        node_by_role[r_name] = n
        children_by_role.setdefault(r_name, [])

    for n in raw_nodes:
        parent = n.get("reports_to", "").strip()
        if parent and parent.lower() != n["role"].lower():
            matched_parent = None
            for p_cand in node_by_role:
                if p_cand.lower() == parent.lower():
                    matched_parent = p_cand
                    break
            if matched_parent:
                children_by_role.setdefault(matched_parent, []).append(n["role"])

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

    # Group nodes by levels using BFS to support arbitrary hierarchy depth
    level_nodes = {}
    node_depth = {}
    visited = set()
    queue = [(root_role, 0)]
    visited.add(root_role.lower())

    while queue:
        curr, depth = queue.pop(0)
        curr_node = node_by_role.get(curr)
        if curr_node:
            level_nodes.setdefault(depth, []).append(curr_node)
            node_depth[curr] = depth
            for ch in children_by_role.get(curr, []):
                if ch.lower() not in visited:
                    visited.add(ch.lower())
                    queue.append((ch, depth + 1))

    # Catch any orphan nodes and assign to Level 1
    for r_name, n in node_by_role.items():
        if r_name.lower() not in visited:
            level_nodes.setdefault(1, []).append(n)
            node_depth[r_name] = 1
            visited.add(r_name.lower())

    max_depth = max(level_nodes.keys()) if level_nodes else 0
    diagram_width = 515
    ceo_node = level_nodes.get(0, [raw_nodes[0]])[0]

    level_1_nodes = level_nodes.get(1, [])
    level_2_nodes = level_nodes.get(2, [])

    has_multi_levels = max_depth >= 2 and len(level_2_nodes) > 0
    two_rows_flat = (not has_multi_levels) and (len(level_1_nodes) > 4)

    card_h = 32 if max_depth >= 4 else 34
    level_gap = 18 if max_depth >= 4 else 22

    num_levels = max_depth + 1
    if num_levels == 1:
        diagram_height = 65
    elif two_rows_flat:
        diagram_height = 175  # CEO + 2 rows of leads
    else:
        diagram_height = 12 + num_levels * card_h + (num_levels - 1) * level_gap + 10

    d = Drawing(diagram_width, diagram_height)

    def draw_role_card(x, y, w, h, role_name, dept_name, priority, is_root=False):
        if is_root:
            bg_col = HexColor("#1E293B")
            border_col = HexColor("#3B82F6")
            title_col = HexColor("#FFFFFF")
            dept_col = HexColor("#93C5FD")
            badge_bg = HexColor("#334155")
            badge_fg = HexColor("#93C5FD")
            badge_text = "LEADER"
        else:
            is_essential = "essential" in str(priority or "").lower()
            bg_col = HexColor("#FFFFFF")
            border_col = HexColor("#2563EB") if is_essential else HexColor("#94A3B8")
            title_col = HexColor("#0F172A")
            dept_col = HexColor("#475569")
            if is_essential:
                badge_bg = HexColor("#DCFCE7")
                badge_fg = HexColor("#166534")
                badge_text = "Essential"
            else:
                badge_bg = HexColor("#FEF3C7")
                badge_fg = HexColor("#92400E")
                badge_text = "Later"

        # Rounded card background
        d.add(Rect(x, y, w, h, rx=4, ry=4, fillColor=bg_col, strokeColor=border_col, strokeWidth=1.2 if is_root else 1.0))

        # Dynamic typography scaling to prevent text clipping
        if w < 90:
            f_size = 6.6
            max_c = 15
            f_dept = 5.8
        elif w < 120:
            f_size = 7.2
            max_c = 20
            f_dept = 6.2
        elif w < 145:
            f_size = 7.8
            max_c = 26
            f_dept = 6.6
        else:
            f_size = 8.2
            max_c = 32
            f_dept = 7.0

        title_str = truncate_text(role_name, max_c)
        d.add(String(x + w / 2, y + h * 0.62, title_str, fontName=FONT_BOLD, fontSize=f_size, fillColor=title_col, textAnchor="middle"))

        # Department (line 2)
        dept_str = truncate_text(dept_name, max_c + 2) if dept_name else ("Executive" if is_root else "General")
        d.add(String(x + w / 2, y + h * 0.38, dept_str, fontName=FONT_REGULAR, fontSize=f_dept, fillColor=dept_col, textAnchor="middle"))

        # Badge pill (line 3)
        badge_w = min(44, w * 0.44)
        badge_h = 8.5
        badge_x = x + (w - badge_w) / 2
        badge_y = y + 2.5
        d.add(Rect(badge_x, badge_y, badge_w, badge_h, rx=2, ry=2, fillColor=badge_bg, strokeColor=None))
        d.add(String(x + w / 2, badge_y + 2.0, badge_text, fontName=FONT_BOLD, fontSize=5.2, fillColor=badge_fg, textAnchor="middle"))

    def draw_down_arrow(x, y_tip):
        d.add(Polygon(
            [x - 3.5, y_tip + 5, x + 3.5, y_tip + 5, x, y_tip],
            fillColor=HexColor("#64748B"),
            strokeColor=HexColor("#64748B"),
        ))

    # 1. Place CEO at the Top Center
    ceo_w = 170
    ceo_h = card_h
    ceo_x = (diagram_width - ceo_w) / 2
    ceo_y = diagram_height - 10 - ceo_h
    ceo_mid_x = ceo_x + ceo_w / 2
    draw_role_card(ceo_x, ceo_y, ceo_w, ceo_h, ceo_node["role"], ceo_node.get("department", "Executive Leadership"), "Essential", is_root=True)

    if num_levels == 1:
        return d

    # 2. Flat Large Team Special Case (Level 1 with > 4 direct reports wrapped in 2 rows)
    if two_rows_flat:
        level_1_nodes = level_nodes.get(1, [])
        num_subs = len(level_1_nodes)
        row1_nodes = level_1_nodes[: (num_subs + 1) // 2]
        row2_nodes = level_1_nodes[(num_subs + 1) // 2 :]

        row1_y = 68
        row2_y = 12

        bus1_y = (ceo_y + row1_y + card_h) / 2
        d.add(Line(ceo_mid_x, ceo_y, ceo_mid_x, bus1_y, strokeColor=HexColor("#64748B"), strokeWidth=1.2))

        def draw_flat_row(nodes, y_pos, bus_level):
            cnt = len(nodes)
            gap = 10
            total_gaps = (cnt - 1) * gap
            avail_w = min(495, diagram_width - 20)
            lw = min(145, (avail_w - total_gaps) / cnt)
            rw = cnt * lw + total_gaps
            sx = (diagram_width - rw) / 2

            centers = []
            for i, node in enumerate(nodes):
                bx = sx + i * (lw + gap)
                draw_role_card(bx, y_pos, lw, card_h, node["role"], node.get("department", "General"), node.get("priority", "Essential"), is_root=False)
                cx = bx + lw / 2
                centers.append(cx)

            if len(centers) > 1:
                d.add(Line(min(centers), bus_level, max(centers), bus_level, strokeColor=HexColor("#64748B"), strokeWidth=1.2))

            for cx in centers:
                d.add(Line(cx, bus_level, cx, y_pos + card_h, strokeColor=HexColor("#64748B"), strokeWidth=1.2))
                draw_down_arrow(cx, y_pos + card_h)

        draw_flat_row(row1_nodes, row1_y, bus1_y)

        bus2_y = (row1_y + row2_y + card_h) / 2
        d.add(Line(ceo_mid_x, bus1_y, ceo_mid_x, bus2_y, strokeColor=HexColor("#64748B"), strokeWidth=1.2))
        draw_flat_row(row2_nodes, row2_y, bus2_y)
        return d

    # 3. Generalized Dynamic Multi-Level Renderer (Supports 1, 2, 3, 4, 5+ Levels)
    # Stores {role_lower: (x_pos, y_pos, width, height, center_x)} for all rendered nodes
    rendered_coords = {
        ceo_node["role"].lower(): (ceo_x, ceo_y, ceo_w, ceo_h, ceo_mid_x)
    }

    for depth in range(1, num_levels):
        y_curr = ceo_y - depth * (card_h + level_gap)
        nodes_curr = level_nodes.get(depth, [])
        if not nodes_curr:
            continue

        # Sort nodes at this level by their parent's horizontal position to prevent crossed lines
        def get_parent_sort_key(node):
            parent_role = node.get("reports_to", "").strip().lower()
            if parent_role in rendered_coords:
                return rendered_coords[parent_role][4]
            return diagram_width / 2

        nodes_curr = sorted(nodes_curr, key=get_parent_sort_key)

        num_curr = len(nodes_curr)
        gap_curr = 10 if num_curr <= 4 else 8
        total_gaps = (num_curr - 1) * gap_curr
        avail_w = min(495, diagram_width - 20)
        w_curr = min(150, max(68, (avail_w - total_gaps) / num_curr))
        total_row_w = num_curr * w_curr + total_gaps
        start_x = (diagram_width - total_row_w) / 2

        # Draw cards for current level
        parent_to_child_centers = {}
        for i, node in enumerate(nodes_curr):
            x_pos = start_x + i * (w_curr + gap_curr)
            mid_x = x_pos + w_curr / 2
            draw_role_card(x_pos, y_curr, w_curr, card_h, node["role"], node.get("department", "General"), node.get("priority", "Essential"), is_root=False)
            rendered_coords[node["role"].lower()] = (x_pos, y_curr, w_curr, card_h, mid_x)

            p_key = node.get("reports_to", "").strip().lower()
            parent_to_child_centers.setdefault(p_key, []).append(mid_x)

        # Draw orthogonal reporting connectors and arrows from each parent to its children
        bus_y = y_curr + card_h + level_gap / 2
        for p_key, child_centers in parent_to_child_centers.items():
            if p_key in rendered_coords:
                p_mid_x = rendered_coords[p_key][4]
                p_bottom_y = rendered_coords[p_key][1]
            else:
                p_mid_x = ceo_mid_x
                p_bottom_y = ceo_y

            # Vertical drop from parent to bus
            d.add(Line(p_mid_x, p_bottom_y, p_mid_x, bus_y, strokeColor=HexColor("#64748B"), strokeWidth=1.2))

            # Horizontal bus spanning parent and children
            bus_min_x = min([p_mid_x] + child_centers)
            bus_max_x = max([p_mid_x] + child_centers)
            if bus_max_x > bus_min_x:
                d.add(Line(bus_min_x, bus_y, bus_max_x, bus_y, strokeColor=HexColor("#64748B"), strokeWidth=1.2))

            # Vertical drops from bus to each child with downward arrow
            for cx in child_centers:
                d.add(Line(cx, bus_y, cx, y_curr + card_h, strokeColor=HexColor("#64748B"), strokeWidth=1.2))
                draw_down_arrow(cx, y_curr + card_h)

    return d


build_team_hierarchy_diagram = build_multi_level_hierarchy_diagram


def build_roadmap_diagram(roadmap_items: list) -> list:
    """Constructs a sequential flowchart diagram representing the startup roadmap."""
    flowables = []
    if not roadmap_items or not isinstance(roadmap_items, list):
        return [Paragraph("<i>No roadmap flow available.</i>", getSampleStyleSheet()["Normal"])]

    steps = [s for s in roadmap_items if isinstance(s, dict)]
    total_steps = len(steps)

    for idx, item in enumerate(steps):
        step_num = item.get("step_number", idx + 1)
        phase_name = truncate_text(item.get("phase_name", f"Phase {step_num}"), 38)
        timeline = truncate_text(item.get("estimated_timeline", ""), 20)
        desc_clean = sanitize_sisfs_and_msme_recommendation(item.get("description", ""))
        desc = truncate_text(desc_clean, 68)

        card_dw = Drawing(510, 48)
        card_dw.add(Rect(15, 2, 480, 44, rx=5, ry=5, fillColor=HexColor("#F8FAFC"), strokeColor=HexColor("#CBD5E1"), strokeWidth=1))
        card_dw.add(Rect(26, 12, 60, 24, rx=3.5, ry=3.5, fillColor=HexColor("#2563EB"), strokeColor=None))
        card_dw.add(String(56, 19, f"Step {step_num}", fontName=FONT_BOLD, fontSize=8.5, fillColor=HexColor("#FFFFFF"), textAnchor="middle"))
        card_dw.add(String(96, 25, phase_name, fontName=FONT_BOLD, fontSize=8.5, fillColor=HexColor("#0F172A")))

        if timeline:
            card_dw.add(String(482, 25, timeline, fontName=FONT_BOLD, fontSize=8.0, fillColor=HexColor("#2563EB"), textAnchor="end"))

        if desc:
            card_dw.add(String(96, 11, desc, fontName=FONT_REGULAR, fontSize=7.5, fillColor=HexColor("#475569")))

        flowables.append(card_dw)

        if idx < total_steps - 1:
            arrow_dw = Drawing(510, 14)
            arrow_dw.add(Line(255, 14, 255, 4, strokeColor=HexColor("#2563EB"), strokeWidth=1.5))
            arrow_dw.add(Polygon([250, 4, 260, 4, 255, 0], fillColor=HexColor("#2563EB"), strokeColor=HexColor("#2563EB")))
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
    tailored to the specific startup idea, industry, business model, and stage.
    Covers all 10 core sections, provides verified links, dynamic multi-level
    hierarchy charts, structured financial analysis, and compliant funding cards.
    """
    report = report or {}

    # Setup running canvas metadata
    st_name = str(report.get("startup_name") or "Startup Venture").strip()
    if st_name.lower() in ["none", "null", "not specified"]:
        st_name = "Target Venture"
    NumberedCanvas.startup_name = st_name
    NumberedCanvas.generated_date = datetime.now().strftime("%B %d, %Y")

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName=FONT_BOLD,
        fontSize=18,
        leading=22,
        textColor=HexColor("#0F172A"),
        alignment=TA_LEFT,
        spaceAfter=3,
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName=FONT_BOLD,
        fontSize=9,
        leading=12,
        textColor=HexColor("#2563EB"),
        alignment=TA_LEFT,
        spaceAfter=8,
    )

    h1_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName=FONT_BOLD,
        fontSize=12,
        leading=15,
        textColor=HexColor("#1E3A8A"),
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True,
    )

    h2_style = ParagraphStyle(
        "SubSectionHeading",
        parent=styles["Normal"],
        fontName=FONT_BOLD,
        fontSize=10,
        leading=13,
        textColor=HexColor("#1D4ED8"),
        spaceBefore=7,
        spaceAfter=4,
        keepWithNext=True,
    )

    item_title_style = ParagraphStyle(
        "ItemTitle",
        parent=styles["Normal"],
        fontName=FONT_BOLD,
        fontSize=9.5,
        leading=13,
        textColor=HexColor("#0F172A"),
        spaceAfter=3,
    )

    body_style = ParagraphStyle(
        "StandardBody",
        parent=styles["Normal"],
        fontName=FONT_REGULAR,
        fontSize=8,
        leading=11.5,
        textColor=HexColor("#1E293B"),
    )

    bullet_style = ParagraphStyle(
        "BulletItem",
        parent=styles["Normal"],
        fontName=FONT_REGULAR,
        fontSize=8,
        leading=11.5,
        textColor=HexColor("#1E293B"),
        leftIndent=10,
        spaceAfter=2,
    )

    card_label_style = ParagraphStyle(
        "CardLabel",
        parent=styles["Normal"],
        fontName=FONT_BOLD,
        fontSize=8,
        leading=11.5,
        textColor=HexColor("#334155"),
        spaceBefore=2,
        spaceAfter=1,
    )

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=46,
        bottomMargin=42,
    )

    story = []
    content_width = 523

    def section_divider():
        return HRFlowable(
            width="100%",
            thickness=0.5,
            color=HexColor("#E2E8F0"),
            spaceBefore=8,
            spaceAfter=8,
        )

    def make_card(flowables_list, border_hex="#CBD5E1", bg_hex="#F8FAFC") -> Table:
        card_table = Table([[flowables_list]], colWidths=[content_width])
        card_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), HexColor(bg_hex)),
            ("BOX", (0, 0), (-1, -1), 0.75, HexColor(border_hex)),
            ("LEFTPADDING", (0, 0), (-1, -1), 9),
            ("RIGHTPADDING", (0, 0), (-1, -1), 9),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ]))
        return card_table

    # -------------------------------------------------------------------------
    # COVER / HEADER BLOCK
    # -------------------------------------------------------------------------
    story.append(Paragraph("Startup Intelligence Report", title_style))
    story.append(Paragraph("AGENTIC AI PERSONALIZED STARTUP MENTOR â€¢ DOMAIN INTELLIGENCE", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=HexColor("#2563EB"), spaceBefore=0, spaceAfter=8))

    startup_name_val = report.get("startup_name")
    industry_val = report.get("industry") or "Technology & Software"
    stage_val = report.get("stage") or "Early Stage / MVP Validation"

    header_meta_p1 = f"<b>Target Startup Idea:</b> {safe_text(startup_idea, 'Not specified')}"
    if startup_name_val and str(startup_name_val).strip() and str(startup_name_val).strip().lower() != "not specified":
        header_meta_p1 = f"<b>Startup Name:</b> {safe_text(startup_name_val)} &nbsp;&nbsp;|&nbsp;&nbsp; " + header_meta_p1

    header_meta_p2 = f"<b>Target Industry:</b> {safe_text(industry_val)} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Current Stage:</b> {safe_text(stage_val)}"

    idea_table = Table(
        [
            [Paragraph(header_meta_p1, body_style)],
            [Paragraph(header_meta_p2, body_style)],
        ],
        colWidths=[content_width],
    )
    idea_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), HexColor("#EFF6FF")),
        ("BOX", (0, 0), (-1, -1), 0.5, HexColor("#93C5FD")),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(idea_table)
    story.append(Spacer(1, 8))

    # -------------------------------------------------------------------------
    # 1. EXECUTIVE SUMMARY
    # -------------------------------------------------------------------------
    story.append(Paragraph("1. Executive Summary", h1_style))
    exec_summary_raw = safe_text(report.get("executive_summary"), "Executive summary not available.")
    exec_summary = sanitize_sisfs_and_msme_recommendation(exec_summary_raw)
    story.append(Paragraph(exec_summary, body_style))
    story.append(section_divider())

    # -------------------------------------------------------------------------
    # 2. STARTUP IDEA AND BUSINESS MODEL
    # -------------------------------------------------------------------------
    story.append(Paragraph("2. Startup Idea and Business Model", h1_style))
    bm_data = report.get("startup_idea_and_business_model") or report.get("business_model") or {}

    bm_elements = []
    if isinstance(bm_data, dict) and bm_data:
        val_prop = safe_text(bm_data.get("value_proposition") or bm_data.get("core_value_proposition"))
        target_cust = safe_text(bm_data.get("target_customers") or bm_data.get("target_users"))
        rev_model = safe_text(bm_data.get("revenue_model") or bm_data.get("monetization_architecture"))
        gtm = safe_text(bm_data.get("go_to_market") or bm_data.get("distribution_strategy"))

        bm_elements.extend([
            Paragraph(f"<b>Core Value Proposition:</b> {val_prop}", body_style),
            Paragraph(f"<b>Target Customers & Segments:</b> {target_cust}", body_style),
            Paragraph(f"<b>Revenue Model & Monetization:</b> {rev_model}", body_style),
            Paragraph(f"<b>Go-To-Market Approach:</b> {gtm}", body_style),
        ])
    else:
        val_prop = safe_text(report.get("value_proposition"), safe_text(startup_idea))
        target_cust = safe_text(report.get("target_customers"), "Early adopters, enterprise pilots, and targeted end-users in sector")
        rev_model = safe_text(report.get("revenue_model"), "Direct B2B/B2C SaaS subscriptions, usage-based metering, or pilot licensing")
        gtm = safe_text(report.get("go_to_market"), "Direct founder-led sales outreach, partner integrations, and content-driven developer/user onboarding")

        bm_elements.extend([
            Paragraph(f"<b>Target Concept & Value Proposition:</b> {val_prop}", body_style),
            Paragraph(f"<b>Primary Target Users / Buyers:</b> {target_cust}", body_style),
            Paragraph(f"<b>Monetization Architecture:</b> {rev_model}", body_style),
            Paragraph(f"<b>Distribution & Go-to-Market Strategy:</b> {gtm}", body_style),
        ])

    story.append(make_card(bm_elements))
    story.append(section_divider())

    # -------------------------------------------------------------------------
    # 3. MARKET AND COMPETITOR ANALYSIS
    # -------------------------------------------------------------------------
    story.append(Paragraph("3. Market and Competitor Analysis", h1_style))
    comp_raw = report.get("competitor_analysis") or report.get("competitors")
    competitors = list(comp_raw) if isinstance(comp_raw, list) else []

    if not competitors:
        story.append(Paragraph("<i>No competitor intelligence recorded for this sector.</i>", body_style))
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
            c_source = safe_text(comp.get("source"), "Public market records")
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

            story.append(KeepTogether([make_card(card_elements), Spacer(1, 5)]))

    # Strategic Differentiation Breakdown
    comparison = report.get("startup_vs_competitors")
    if comparison:
        story.append(Spacer(1, 4))
        story.append(Paragraph("Strategic Differentiation vs. Competitors", h2_style))
        comp_diff_elements = []
        if isinstance(comparison, list):
            for point in comparison:
                if isinstance(point, dict):
                    c_target = safe_text(point.get("competitor") or point.get("name"), "Market Alternative")
                    diff = safe_text(point.get("differentiation") or point.get("comparison"), "")
                    comp_diff_elements.append(Paragraph(f"â€¢ <b>vs {c_target}:</b> {diff}", bullet_style))
                else:
                    comp_diff_elements.append(Paragraph(f"â€¢ {safe_text(point)}", bullet_style))
        elif isinstance(comparison, dict):
            for k, v in comparison.items():
                comp_diff_elements.append(Paragraph(f"â€¢ <b>{safe_text(k)}:</b> {safe_text(v)}", bullet_style))
        else:
            comp_diff_elements.append(Paragraph(f"â€¢ {safe_text(comparison)}", bullet_style))

        story.append(make_card(comp_diff_elements))

    story.append(section_divider())

    # -------------------------------------------------------------------------
    # 4. FUNDING AND GOVERNMENT SCHEMES
    # -------------------------------------------------------------------------
    story.append(Paragraph("4. Funding and Government Schemes", h1_style))

    gov_raw = report.get("government_funding_schemes")
    gov_funding = list(gov_raw) if isinstance(gov_raw, list) else []

    priv_raw = report.get("private_funding_opportunities")
    priv_funding = list(priv_raw) if isinstance(priv_raw, list) else []

    # Backward compatibility fallback
    if not gov_funding and not priv_funding:
        fallback_raw = report.get("funding_opportunities")
        fallback_funding = list(fallback_raw) if isinstance(fallback_raw, list) else []
        if fallback_funding:
            for item in fallback_funding:
                if not isinstance(item, dict):
                    continue
                combined = f"{item.get('funding_type', '')} {item.get('organization', '')} {item.get('name', '')}".lower()
                gov_keywords = ["gov", "ministry", "dpiit", "birac", "meity", "msme", "sidbi", "dst", "startup india", "sisfs", "state"]
                if any(k in combined for k in gov_keywords):
                    gov_funding.append(item)
                else:
                    priv_funding.append(item)

    def render_funding_card(opp: dict, is_government: bool = True):
        name = safe_text(opp.get("name") or opp.get("scheme_name"), "Funding Opportunity")
        org = safe_text(opp.get("organization") or opp.get("implementing_agency"), "Implementing Agency" if is_government else "Organization / Program")
        funding_type = safe_text(opp.get("funding_type"), "Grant" if is_government else "Private Capital / Program")
        amount = safe_text(opp.get("funding_amount") or opp.get("amount"), "Not publicly verified")
        stage = safe_text(opp.get("startup_stage") or opp.get("stage"), "Early / Validation")
        deadline_raw = safe_text(opp.get("deadline") or opp.get("status"), "Not publicly specified")
        status_raw = str(opp.get("status") or "")
        evidence_raw = str(opp.get("official_source_evidence") or opp.get("status_evidence") or "")

        status_label, badge_bg, badge_fg, border_hex, card_bg_hex, deadline_text = get_opportunity_status(
            name, deadline_raw, status_raw, evidence_raw
        )

        eligibility = safe_text(opp.get("eligibility"))
        who_can_apply = safe_text(opp.get("who_can_apply"))
        usage = safe_text(opp.get("usage") or opp.get("permitted_fund_usage"))
        why_suitable = safe_text(opp.get("why_suitable") or opp.get("suitability"))
        where_to_apply = safe_text(opp.get("where_to_apply") or opp.get("application_portal"))
        app_website = opp.get("application_website") or opp.get("website") or ""

        if "msme" in name.lower() and not app_website:
            app_website = "https://innovative.msme.gov.in"

        source_name = safe_text(opp.get("official_source_name") or opp.get("official_source"), org)
        source_url = opp.get("official_source_url") or opp.get("source_url") or ""

        steps = opp.get("application_steps", [])
        docs = opp.get("required_documents", [])

        # Sanitize mentions
        eligibility = sanitize_sisfs_and_msme_recommendation(eligibility)
        who_can_apply = sanitize_sisfs_and_msme_recommendation(who_can_apply)
        usage = sanitize_sisfs_and_msme_recommendation(usage)
        why_suitable = sanitize_sisfs_and_msme_recommendation(why_suitable)
        where_to_apply = sanitize_sisfs_and_msme_recommendation(where_to_apply)
        if isinstance(steps, list):
            steps = [sanitize_sisfs_and_msme_recommendation(str(s)) for s in steps]
        elif isinstance(steps, str):
            steps = sanitize_sisfs_and_msme_recommendation(steps)
        if isinstance(docs, list):
            docs = [sanitize_sisfs_and_msme_recommendation(str(d)) for d in docs]
        elif isinstance(docs, str):
            docs = sanitize_sisfs_and_msme_recommendation(docs)

        status_badge_html = f'<font color="{badge_fg}"><b>[{status_label}]</b></font>'

        card_elements = [
            Paragraph(f"<b>{name}</b> &nbsp;&nbsp; {status_badge_html}", item_title_style),
            Spacer(1, 2),
            Paragraph(f"<b>Implementing Agency / Organization:</b> {org} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Funding Type:</b> {funding_type}", body_style),
            Paragraph(f"<b>Funding Amount:</b> {amount} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Target Stage:</b> {stage}", body_style),
            Paragraph(f"<b>Current Status / Deadline:</b> {deadline_text}", body_style),
            Spacer(1, 2),
            HRFlowable(width="100%", thickness=0.5, color=HexColor("#E2E8F0"), spaceBefore=2, spaceAfter=3),
            Paragraph(f"<b>Eligibility Criteria:</b> {eligibility}", body_style),
            Paragraph(f"<b>Who Can Apply:</b> {who_can_apply}", body_style),
            Paragraph(f"<b>Permitted Fund Usage:</b> {usage}", body_style),
            Paragraph(f"<b>Strategic Fit & Suitability:</b> {why_suitable}", body_style),
            Paragraph(f"<b>Where to Apply:</b> {where_to_apply}", body_style),
            Paragraph(f"<b>Application Portal Link:</b> {make_clickable_link(app_website, app_website)}", body_style),
        ]

        if source_url:
            card_elements.append(Paragraph(f"<b>Official Source:</b> {source_name} &nbsp;|&nbsp; <b>Official Link:</b> {make_clickable_link(source_url, source_url)}", body_style))
        else:
            card_elements.append(Paragraph(f"<b>Official Source:</b> {source_name}", body_style))

        card_elements.append(Spacer(1, 2))
        card_elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#E2E8F0"), spaceBefore=2, spaceAfter=3))

        # Application Steps
        card_elements.append(Paragraph("<b>Step-by-Step Application Procedure:</b>", card_label_style))
        if steps and isinstance(steps, list):
            for s_idx, step_val in enumerate(steps, 1):
                card_elements.append(Paragraph(f"&nbsp;&nbsp;<b>Step {s_idx}:</b> {safe_text(step_val)}", bullet_style))
        elif isinstance(steps, str) and steps.strip():
            card_elements.append(Paragraph(f"&nbsp;&nbsp;{safe_text(steps)}", bullet_style))
        else:
            card_elements.append(Paragraph("&nbsp;&nbsp;Refer to official portal guidelines.", bullet_style))

        # Required Documents Checklist
        card_elements.append(Spacer(1, 1))
        card_elements.append(Paragraph("<b>Required Documents Checklist:</b>", card_label_style))
        if docs and isinstance(docs, list):
            doc_items = ", ".join([safe_text(d) for d in docs])
            card_elements.append(Paragraph(f"&nbsp;&nbsp;â€¢ {doc_items}", bullet_style))
        elif isinstance(docs, str) and docs.strip():
            card_elements.append(Paragraph(f"&nbsp;&nbsp;â€¢ {safe_text(docs)}", bullet_style))
        else:
            card_elements.append(Paragraph("&nbsp;&nbsp;â€¢ As specified on the official application portal.", bullet_style))

        card_flowable = make_card(card_elements, border_hex=border_hex, bg_hex=card_bg_hex)
        return KeepTogether([card_flowable, Spacer(1, 6)])

    # 4A. Government Funding Schemes
    story.append(Paragraph("A. Government Funding Schemes", h2_style))
    if not gov_funding:
        story.append(Paragraph("<i>No government funding schemes recorded for this sector.</i>", body_style))
    else:
        for opp in gov_funding:
            if isinstance(opp, dict):
                story.append(render_funding_card(opp, is_government=True))

    story.append(Spacer(1, 4))

    # 4B. Private Funding Opportunities
    story.append(Paragraph("B. Private Funding Opportunities & Accelerators", h2_style))
    if not priv_funding:
        story.append(Paragraph("<i>No private funding opportunities recorded for this sector.</i>", body_style))
    else:
        for opp in priv_funding:
            if isinstance(opp, dict):
                story.append(render_funding_card(opp, is_government=False))

    story.append(section_divider())

    # -------------------------------------------------------------------------
    # 5. COMPANY AND TEAM STRUCTURE
    # -------------------------------------------------------------------------
    story.append(Paragraph("5. Company and Team Structure", h1_style))
    team_raw = report.get("recommended_team_structure") or report.get("team_structure")
    team_list = list(team_raw) if isinstance(team_raw, list) else []

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

                story.append(KeepTogether([make_card(card_elements), Spacer(1, 4)]))

        render_role_cards(essential_roles, "Essential Roles (Immediate / MVP Stage)")
        render_role_cards(later_roles, "Roles That Can Be Added Later (Scale / Expansion Stage)")

    # Lean Team Advice Card
    lean_advice = report.get("lean_team_advice") or report.get("team_recommendation")
    if lean_advice:
        story.append(Spacer(1, 3))
        story.append(Paragraph("Lean Team Execution Strategy", h2_style))
        story.append(make_card([Paragraph(safe_text(lean_advice), body_style)]))

    # Dynamic Organizational Hierarchy Diagram (Supports all depths, 1 to 5+ levels)
    hierarchy_raw = report.get("team_hierarchy")
    hierarchy_nodes = list(hierarchy_raw) if isinstance(hierarchy_raw, list) else []

    story.append(Spacer(1, 6))
    story.append(Paragraph("Dynamic Organizational Hierarchy", h2_style))
    story.append(Paragraph("<i>Organizational reporting structure mapped from CEO down through all operational tiers:</i>", body_style))
    story.append(Spacer(1, 4))

    hierarchy_diagram = build_multi_level_hierarchy_diagram(
        hierarchy_nodes,
        team_list,
    )
    story.append(KeepTogether([hierarchy_diagram, Spacer(1, 6)]))

    story.append(section_divider())

    # -------------------------------------------------------------------------
    # 6. FINANCIAL ANALYSIS
    # -------------------------------------------------------------------------
    story.append(Paragraph("6. Financial Analysis", h1_style))
    fin_info = report.get("financial_analysis") or report.get("financial_information") or report.get("financials")

    if not fin_info:
        story.append(Paragraph("<i>Financial Analysis: Domain estimates and historical figures not publicly verified.</i>", body_style))
    else:
        fin_elements = []
        if isinstance(fin_info, dict):
            for k, v in fin_info.items():
                label = safe_text(k).replace("_", " ").title()
                if isinstance(v, list):
                    fin_elements.append(Paragraph(f"<b>{label}:</b>", card_label_style))
                    for item in v:
                        fin_elements.append(Paragraph(f"â€¢ {safe_text(item)}", bullet_style))
                else:
                    fin_elements.append(Paragraph(f"â€¢ <b>{label}:</b> {safe_text(v)}", bullet_style))
        elif isinstance(fin_info, list):
            for item in fin_info:
                if isinstance(item, dict):
                    rev = safe_text(item.get("revenue"), "Not verified")
                    pl = safe_text(item.get("profit_loss"), "Not verified")
                    funding = safe_text(item.get("funding_raised"), "Not verified")
                    src = safe_text(item.get("source"), "Public filing")
                    fin_elements.append(Paragraph(f"â€¢ <b>Revenue:</b> {rev} | <b>Profit/Loss:</b> {pl} | <b>Funding Raised:</b> {funding} (Source: {src})", bullet_style))
                else:
                    fin_elements.append(Paragraph(f"â€¢ {safe_text(item)}", bullet_style))
        else:
            fin_elements.append(Paragraph(f"â€¢ {safe_text(fin_info)}", bullet_style))

        fin_elements.append(Spacer(1, 2))
        fin_elements.append(Paragraph("<i>Note: Figures and timelines are illustrative estimates and planning assumptions based on domain benchmarks, not guaranteed financial forecasts.</i>", bullet_style))

        story.append(make_card(fin_elements))

    story.append(section_divider())

    # -------------------------------------------------------------------------
    # 7. RISK ANALYSIS
    # -------------------------------------------------------------------------
    story.append(Paragraph("7. Risk Analysis", h1_style))
    risk_info = report.get("risk_analysis") or report.get("risks")

    if not risk_info:
        story.append(Paragraph("<i>Risk analysis not specified for this venture.</i>", body_style))
    else:
        risk_elements = []
        if isinstance(risk_info, list):
            for r in risk_info:
                if isinstance(r, dict):
                    cat = safe_text(r.get("category") or r.get("risk_type"), "Risk")
                    desc = safe_text(r.get("description") or r.get("risk"))
                    mit = safe_text(r.get("mitigation") or r.get("mitigation_strategy"), "Active monitoring")
                    risk_elements.append(Paragraph(f"â€¢ <b>{cat}:</b> {desc}", bullet_style))
                    risk_elements.append(Paragraph(f"&nbsp;&nbsp;<b>Mitigation:</b> {mit}", bullet_style))
                else:
                    risk_elements.append(Paragraph(f"â€¢ {safe_text(r)}", bullet_style))
        elif isinstance(risk_info, dict):
            for k, v in risk_info.items():
                label = safe_text(k).replace("_", " ").title()
                risk_elements.append(Paragraph(f"â€¢ <b>{label}:</b> {safe_text(v)}", bullet_style))
        else:
            risk_elements.append(Paragraph(f"â€¢ {safe_text(risk_info)}", bullet_style))

        story.append(make_card(risk_elements))

    story.append(section_divider())

    # -------------------------------------------------------------------------
    # 8. STARTUP-SPECIFIC ROADMAP
    # -------------------------------------------------------------------------
    story.append(Paragraph("8. Startup-Specific Roadmap", h1_style))
    road_raw = report.get("roadmap") or report.get("startup_roadmap")
    roadmap_list = list(road_raw) if isinstance(road_raw, list) else []

    if not roadmap_list:
        story.append(Paragraph("<i>Roadmap details not available.</i>", body_style))
    else:
        for idx, r_step in enumerate(roadmap_list, 1):
            if not isinstance(r_step, dict):
                continue
            s_num = safe_text(r_step.get("step_number", idx))
            s_phase = safe_text(r_step.get("phase_name", f"Phase {s_num}"))
            s_time = safe_text(r_step.get("estimated_timeline"))
            s_desc_raw = safe_text(r_step.get("description"))
            s_desc = sanitize_sisfs_and_msme_recommendation(s_desc_raw)

            step_elements = [
                Paragraph(f"<b>Phase {s_num}: {s_phase}</b> &nbsp;<font color='#2563EB'>({s_time})</font>", item_title_style),
                Spacer(1, 2),
                Paragraph(s_desc, body_style),
            ]

            deliv = r_step.get("deliverables")
            if deliv:
                d_text = ", ".join([safe_text(d) for d in deliv]) if isinstance(deliv, list) else safe_text(deliv)
                step_elements.append(Paragraph(f"<b>Key Deliverables:</b> {d_text}", body_style))

            story.append(KeepTogether([make_card(step_elements), Spacer(1, 4)]))

        story.append(Spacer(1, 6))
        story.append(Paragraph("<b>Startup Execution Flowchart:</b>", card_label_style))
        story.append(Spacer(1, 4))
        diagram_flowables = build_roadmap_diagram(roadmap_list)
        if len(diagram_flowables) <= 8:
            story.append(KeepTogether(diagram_flowables))
        else:
            for df in diagram_flowables:
                story.append(df)

    story.append(section_divider())

    # -------------------------------------------------------------------------
    # 9. RECOMMENDATIONS AND NEXT ACTIONS
    # -------------------------------------------------------------------------
    story.append(Paragraph("9. Recommendations and Next Actions", h1_style))
    recommendations = report.get("important_recommendations") or report.get("recommendations") or report.get("next_actions")

    if not recommendations:
        story.append(Paragraph("<i>Recommendations not available.</i>", body_style))
    else:
        rec_elements = []
        if isinstance(recommendations, list):
            for idx, rec in enumerate(recommendations, 1):
                cleaned_rec = sanitize_sisfs_and_msme_recommendation(str(rec))
                rec_elements.append(Paragraph(f"<b>{idx}.</b> {safe_text(cleaned_rec)}", bullet_style))
        else:
            cleaned_rec = sanitize_sisfs_and_msme_recommendation(str(recommendations))
            rec_elements.append(Paragraph(safe_text(cleaned_rec), bullet_style))
        story.append(make_card(rec_elements))

    story.append(section_divider())

    # -------------------------------------------------------------------------
    # 10. PROFESSIONAL NETWORKS AND USEFUL LINKS
    # -------------------------------------------------------------------------
    story.append(Paragraph("10. Professional Networks and Useful Links", h1_style))
    src_raw = (
        report.get("professional_networks_and_links")
        or report.get("professional_networks")
        or report.get("sources")
        or report.get("useful_links")
    )
    sources_list = list(src_raw) if isinstance(src_raw, list) else []

    source_elements = []

    # 1. Official Company Setup Presence Link
    source_elements.append(Paragraph("â€¢ <b>LinkedIn Company Page Setup:</b> Establish official venture page", bullet_style))
    source_elements.append(Paragraph(f"&nbsp;&nbsp;<b>Link:</b> {make_clickable_link('https://www.linkedin.com/company/setup/new/', 'https://www.linkedin.com/company/setup/new/')}", bullet_style))
    source_elements.append(Spacer(1, 3))

    if sources_list:
        for src in sources_list:
            if isinstance(src, dict):
                src_name = safe_text(src.get("name") or src.get("title"), "Verified Resource")
                src_type = safe_text(src.get("source_type") or src.get("type"), "")
                src_cat = safe_text(src.get("category"), "")
                src_url = src.get("url") or ""

                meta_line = []
                if src_type and src_type.lower() not in ["not available", "none"]:
                    meta_line.append(f"<b>Type:</b> {src_type}")
                if src_cat and src_cat.lower() not in ["not available", "none"]:
                    meta_line.append(f"<b>Category:</b> {src_cat}")

                meta_str = f" &nbsp;|&nbsp; {' &nbsp;|&nbsp; '.join(meta_line)}" if meta_line else ""
                source_elements.append(Paragraph(f"â€¢ <b>{src_name}</b>{meta_str}", bullet_style))
                source_elements.append(Paragraph(f"&nbsp;&nbsp;<b>Link:</b> {make_clickable_link(src_url, src_url)}", bullet_style))
            elif isinstance(src, str):
                source_elements.append(Paragraph(f"â€¢ <b>Resource:</b> {make_clickable_link(src, src)}", bullet_style))

    story.append(make_card(source_elements))

    doc.build(story, canvasmaker=NumberedCanvas)
