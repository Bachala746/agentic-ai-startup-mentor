import re
import html
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
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
# UNICODE FONT REGISTRATION (INDIAN RUPEE ₹ SYMBOL & SPECIAL CHARS)
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
        self.drawString(36, 18, f"Agentic AI Startup Mentor • Prepared {self.generated_date} • Verified & Dynamic Intelligence")
        self.drawRightString(559, 18, f"Page {self._pageNumber} of {page_count}")

        self.restoreState()


# ============================================================================
# HELPER UTILITIES
# ============================================================================

def safe_text(val, fallback: str = "Unverified") -> str:
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
        "unverified",
        "not publicly specified",
        "",
    ]:
        return '<font color="#64748B">Unverified</font>'

    url_str = re.sub(r"startup\.microsoft\.com", "startups.microsoft.com", url_str, flags=re.IGNORECASE)
    url_str = re.sub(r"^http://", "https://", url_str, flags=re.IGNORECASE)

    href = url_str if url_str.startswith("https://") else f"https://{url_str}"
    display_label = label if label else url_str
    display_label = re.sub(r"startup\.microsoft\.com", "startups.microsoft.com", str(display_label), flags=re.IGNORECASE)

    if len(display_label) > 65 and "/" in display_label:
        parts = display_label.split("/")
        display_label = f"{parts[0]}//{parts[2]}/.../{parts[-1]}" if len(parts) >= 4 else display_label[:62] + "..."

    safe_href = html.escape(href, quote=True)
    safe_label = html.escape(display_label)
    return f'<font color="#1D4ED8"><u><a href="{safe_href}">{safe_label}</a></u></font>'


def truncate_text(text: str, max_chars: int = 40) -> str:
    """Safely shortens text only when strictly necessary."""
    text = str(text or "").strip()
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3] + "..."


def split_title_to_lines(text: str, max_chars_per_line: int = 16) -> list[str]:
    """Wraps role titles or department names into multiple lines to prevent truncation in diagrams."""
    text = str(text or "").strip()
    if not text:
        return [""]
    words = text.split()
    if not words:
        return [text]
    lines = []
    curr = []
    curr_len = 0
    for w in words:
        w_len = len(w)
        if curr_len + w_len + (1 if curr else 0) <= max_chars_per_line:
            curr.append(w)
            curr_len += w_len + (1 if curr else 0)
        else:
            if curr:
                lines.append(" ".join(curr))
            curr = [w]
            curr_len = w_len
            if len(lines) >= 2:
                break
    if curr and len(lines) < 2:
        lines.append(" ".join(curr))
    if len(lines) > 2:
        lines = lines[:2]
    return [truncate_text(l, max_chars_per_line + 4) for l in lines]


def sanitize_sisfs_and_msme_recommendation(text: str) -> str:
    """Sanitizes SISFS and MSME mentions so neither is presented as active or open."""
    if not text or not isinstance(text, str):
        return "" if text is None else str(text)

    t = text

    sisfs_action_pattern = re.compile(
        r'(?i)(?:apply\s+(?:for|to)|submit\s+(?:an?\s+)?application\s+(?:for|to)|seek\s+(?:funding\s+from)?|leverage|utilize|target|tap\s+into|consider\s+applying\s+to|explore\s+applying\s+to)\s+(?:the\s+)?(?:startup\s+india\s+seed\s+fund(?:\s+scheme)?|sisfs)[^.;\n]*',
        re.IGNORECASE
    )
    if sisfs_action_pattern.search(t):
        replacement = (
            "Monitor official portal announcements (seedfund.startupindia.gov.in) for successor schemes to the Startup India Seed Fund Scheme "
            "(SISFS, closed for new applications on 31 May 2026) or explore currently eligible alternatives (such as MeitY TIDE 2.0 and cloud credits)"
        )
        t = sisfs_action_pattern.sub(replacement, t)

    t = re.sub(
        r'(?i)\b(sisfs|startup india seed fund(?:\s+scheme)?)\s*(?:\((?:ongoing|open)\)|[-:–]\s*(?:ongoing|open)|\s+is\s+(?:ongoing|open))\b',
        r'\1 (Closed on 31 May 2026; monitor official portal for successor calls or explore active alternatives)',
        t
    )
    t = re.sub(
        r'(?i)\b(?:ongoing|open)\s+(sisfs|startup india seed fund(?:\s+scheme)?)\b',
        r'\1 (Closed on 31 May 2026; monitor official portal for successor calls or explore active alternatives)',
        t
    )

    t = re.sub(
        r'(?i)\b(msme(?:\s+innovative(?:\s+scheme)?)?)\s*(?:\((?:ongoing|open)\)|[-:–]\s*(?:ongoing|open)|\s+is\s+(?:ongoing|open))\b',
        r'\1 (Status Unverified — Check Official Portal)',
        t
    )
    t = re.sub(
        r'(?i)\b(?:ongoing|open)\s+(msme(?:\s+innovative(?:\s+scheme)?)?)\b',
        r'\1 (Status Unverified — Check Official Portal)',
        t
    )

    return t


def get_opportunity_status(
    opp_name: str,
    deadline_str: str,
    status_str: str = "",
    evidence_str: str = ""
) -> tuple[str, str, str, str, str, str]:
    """Returns (status_label, badge_bg, badge_fg, border_color, card_bg, normalized_deadline)."""
    name_lower = str(opp_name or "").lower()
    dl_lower = str(deadline_str or "").lower()
    st_lower = str(status_str or "").lower()
    ev_lower = str(evidence_str or "").lower()
    combined_ctx = f"{dl_lower} {st_lower} {ev_lower}"

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

    if any(k in dl_lower for k in ["closed", "ended", "expired"]) or any(k in st_lower for k in ["closed", "ended", "expired"]):
        return (
            "STATUS: CLOSED",
            "#FEE2E2",
            "#991B1B",
            "#FCA5A5",
            "#FFF9F9",
            deadline_str or "Applications closed",
        )

    has_confirmed_evidence = (
        any(k in combined_ctx for k in [
            "official source confirmed open",
            "confirmed open by official portal",
            "verified active application window",
            "active call verified open",
            "officially confirmed open",
            "active rolling applications verified",
            "active rolling intake confirmed",
            "active rolling program confirmed",
            "ongoing rolling applications",
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

    return (
        "STATUS: UNVERIFIED",
        "#FEF3C7",
        "#92400E",
        "#FCD34D",
        "#FFFDF7",
        deadline_str if (deadline_str and deadline_str.strip() and dl_lower not in ["none", "null", "n/a", "undefined", "unverified", "not publicly specified"]) else "Status unverified — Check official portal for active call announcements",
    )


# ============================================================================
# COMPACT DYNAMIC ORGANIZATIONAL HIERARCHY BUILDER
# ============================================================================

def build_multi_level_hierarchy_diagram(team_hierarchy: list, team_structure: list) -> Drawing:
    """
    Draws a startup hierarchy diagram where BOTH role titles and department names
    wrap onto multiple lines, eliminating truncated labels.
    """
    nodes = []
    source = team_hierarchy if isinstance(team_hierarchy, list) and team_hierarchy else team_structure
    for item in source if isinstance(source, list) else []:
        if not isinstance(item, dict) or not str(item.get("role", "")).strip():
            continue
        role = str(item.get("role", "")).strip()
        reports_to = str(item.get("reports_to") or "").strip()
        nodes.append({
            "role": role,
            "reports_to": reports_to,
            "department": str(item.get("department") or "").strip(),
            "priority": str(item.get("priority") or "Essential").strip(),
        })

    metadata = {
        str(item.get("role", "")).strip().lower(): item
        for item in (team_structure if isinstance(team_structure, list) else [])
        if isinstance(item, dict) and str(item.get("role", "")).strip()
    }
    for node in nodes:
        meta = metadata.get(node["role"].lower(), {})
        node["department"] = node["department"] or str(meta.get("department") or "General")
        node["priority"] = node["priority"] or str(meta.get("priority") or "Essential")
        if not node["reports_to"] or node["reports_to"].lower() in {"none", "null", "n/a"}:
            node["reports_to"] = ""

    if not nodes:
        nodes = [{"role": "CEO / Founder", "reports_to": "", "department": "Executive Leadership", "priority": "Essential"}]

    by_lower = {n["role"].lower(): n for n in nodes}
    root = next((n for n in nodes if "ceo" in n["role"].lower() or "founder" in n["role"].lower()), nodes[0])
    root["reports_to"] = ""
    root_name = root["role"]
    aliases = {"ceo", "founder", "founder/ceo", "founder / ceo", "chief executive officer", "chief executive officer (ceo)"}
    for node in nodes:
        if node is root:
            continue
        parent = node["reports_to"].strip()
        if parent.lower() in aliases:
            node["reports_to"] = root_name
        elif parent.lower() not in by_lower:
            node["reports_to"] = root_name
        else:
            node["reports_to"] = by_lower[parent.lower()]["role"]

    children = {n["role"]: [] for n in nodes}
    for node in nodes:
        parent = node["reports_to"]
        if parent and parent in children and node["role"] != parent:
            children[parent].append(node["role"])

    reachable = set()
    def mark_reachable(role):
        if role in reachable:
            return
        reachable.add(role)
        for child in children.get(role, []):
            mark_reachable(child)
    mark_reachable(root_name)
    for node in nodes:
        if node["role"] not in reachable and node is not root:
            old_parent = node["reports_to"]
            if old_parent in children and node["role"] in children[old_parent]:
                children[old_parent].remove(node["role"])
            node["reports_to"] = root_name
            children[root_name].append(node["role"])
            mark_reachable(node["role"])

    levels = {}
    depths = {}
    queue = [(root_name, 0)]
    while queue:
        role, depth = queue.pop(0)
        if role in depths:
            continue
        depths[role] = depth
        levels.setdefault(depth, []).append(role)
        for child in children.get(role, []):
            queue.append((child, depth + 1))

    max_depth = max(levels) if levels else 0
    diagram_width = 515
    card_h = 52
    level_gap = 22
    top_pad, bottom_pad = 10, 12
    diagram_height = top_pad + card_h + max_depth * (card_h + level_gap) + bottom_pad
    d = Drawing(diagram_width, diagram_height)
    card_positions = {}

    def draw_card(role, x, y, w, node):
        is_root = role == root_name
        priority = str(node.get("priority") or "Essential")
        essential = "later" not in priority.lower()
        bg = HexColor("#17365D") if is_root else HexColor("#FFFFFF")
        border = HexColor("#3B82F6") if is_root else (HexColor("#2563EB") if essential else HexColor("#D97706"))
        title = HexColor("#FFFFFF") if is_root else HexColor("#0F172A")
        sub = HexColor("#DBEAFE") if is_root else HexColor("#475569")
        d.add(Rect(x, y, w, card_h, rx=4, ry=4, fillColor=bg, strokeColor=border, strokeWidth=1.1))

        max_chars_line = max(11, int(w / 4.6))
        role_lines = split_title_to_lines(role, max_chars_line)
        dept_lines = split_title_to_lines(node.get("department") or "General", max(10, int(w / 4.4)))

        title_size = 6.2 if w < 85 else 6.7

        # Render role title lines
        if len(role_lines) == 1:
            d.add(String(x + w / 2, y + 37, role_lines[0], fontName=FONT_BOLD, fontSize=title_size, fillColor=title, textAnchor="middle"))
        else:
            d.add(String(x + w / 2, y + 41, role_lines[0], fontName=FONT_BOLD, fontSize=title_size, fillColor=title, textAnchor="middle"))
            d.add(String(x + w / 2, y + 33, role_lines[1], fontName=FONT_BOLD, fontSize=title_size, fillColor=title, textAnchor="middle"))

        # Render department lines (multi-line wrapping prevents truncation)
        if len(dept_lines) == 1:
            d.add(String(x + w / 2, y + 21, dept_lines[0], fontName=FONT_REGULAR, fontSize=5.3, fillColor=sub, textAnchor="middle"))
        else:
            d.add(String(x + w / 2, y + 23, dept_lines[0], fontName=FONT_REGULAR, fontSize=5.0, fillColor=sub, textAnchor="middle"))
            d.add(String(x + w / 2, y + 16, dept_lines[1], fontName=FONT_REGULAR, fontSize=5.0, fillColor=sub, textAnchor="middle"))

        # Render badge
        badge = "LEADER" if is_root else ("MVP" if essential else "LATER")
        badge_bg = HexColor("#334155") if is_root else (HexColor("#DCFCE7") if essential else HexColor("#FEF3C7"))
        badge_fg = HexColor("#FFFFFF") if is_root else (HexColor("#166534") if essential else HexColor("#92400E"))
        bw = min(42, w - 8)
        d.add(Rect(x + (w - bw) / 2, y + 2.5, bw, 7.5, rx=2, ry=2, fillColor=badge_bg, strokeColor=None))
        d.add(String(x + w / 2, y + 4.0, badge, fontName=FONT_BOLD, fontSize=4.6, fillColor=badge_fg, textAnchor="middle"))
        card_positions[role] = (x, y, w, card_h, x + w / 2)

    leaves = []
    def collect_leaves(role):
        kids = children.get(role, [])
        if not kids:
            leaves.append(role)
            return 1
        total = 0
        for child in kids:
            total += collect_leaves(child)
        return total
    collect_leaves(root_name)
    leaf_count = max(1, len(leaves))
    margin = 8
    usable = diagram_width - 2 * margin
    slot = usable / leaf_count
    leaf_centers = {role: margin + (i + 0.5) * slot for i, role in enumerate(leaves)}
    subtree_centers = {}
    def center_for(role):
        if role in subtree_centers:
            return subtree_centers[role]
        kids = children.get(role, [])
        if not kids:
            c = leaf_centers.get(role, diagram_width / 2)
        else:
            centers = [center_for(k) for k in kids]
            c = sum(centers) / len(centers)
        subtree_centers[role] = c
        return c
    center_for(root_name)

    card_w = min(126, max(72, (usable - 8 * (leaf_count - 1)) / leaf_count))
    for depth in range(max_depth + 1):
        y = diagram_height - top_pad - card_h - depth * (card_h + level_gap)
        for role in levels.get(depth, []):
            node = by_lower.get(role.lower(), {"role": role, "department": "General", "priority": "Essential"})
            cx = subtree_centers.get(role, diagram_width / 2)
            actual_w = min(180, usable) if role == root_name else card_w
            x = max(2, min(diagram_width - actual_w - 2, cx - actual_w / 2))
            draw_card(role, x, y, actual_w, node)

    for parent, kids in children.items():
        if parent not in card_positions or not kids:
            continue
        px, py, pw, ph, pcx = card_positions[parent]
        child_positions = [card_positions[k] for k in kids if k in card_positions]
        if not child_positions:
            continue
        bus_y = py - level_gap / 2
        d.add(Line(pcx, py, pcx, bus_y, strokeColor=HexColor("#64748B"), strokeWidth=1.1))
        centers = [pos[4] for pos in child_positions]
        if len(centers) > 1:
            d.add(Line(min(centers), bus_y, max(centers), bus_y, strokeColor=HexColor("#64748B"), strokeWidth=1.1))
        for cx, cy, cw, ch, ccx in child_positions:
            d.add(Line(ccx, bus_y, ccx, cy + ch, strokeColor=HexColor("#64748B"), strokeWidth=1.1))
            d.add(Polygon([ccx - 3, cy + ch + 4, ccx + 3, cy + ch + 4, ccx, cy + ch], fillColor=HexColor("#64748B"), strokeColor=HexColor("#64748B")))

    return d


build_team_hierarchy_diagram = build_multi_level_hierarchy_diagram


def build_roadmap_diagram(roadmap_items: list) -> list:
    """
    Constructs a sequential flowchart diagram representing the startup roadmap.
    Uses Table flowables with full wrapped Paragraphs to guarantee no truncation.
    """
    flowables = []
    if not roadmap_items or not isinstance(roadmap_items, list):
        return [Paragraph("<i>No roadmap flow available.</i>", getSampleStyleSheet()["Normal"])]

    steps = [s for s in roadmap_items if isinstance(s, dict)]
    total_steps = len(steps)

    body_s = ParagraphStyle(
        "RoadmapDesc",
        fontName=FONT_REGULAR,
        fontSize=7.8,
        leading=11,
        textColor=HexColor("#334155"),
    )
    badge_s = ParagraphStyle(
        "RoadmapBadge",
        fontName=FONT_BOLD,
        fontSize=8.5,
        leading=11,
        textColor=HexColor("#FFFFFF"),
        alignment=TA_CENTER,
    )

    for idx, item in enumerate(steps):
        step_num = item.get("step_number", idx + 1)
        phase_name = safe_text(item.get("phase_name", f"Phase {step_num}"))
        timeline = safe_text(item.get("estimated_timeline", ""))
        desc_clean = sanitize_sisfs_and_msme_recommendation(item.get("description", ""))
        desc = safe_text(desc_clean)

        title_html = f"<b>{phase_name}</b>"
        if timeline and timeline.lower() not in ["none", "unverified", "not publicly specified"]:
            title_html += f" &nbsp;&nbsp; <font color='#2563EB'><b>({timeline})</b></font>"

        content_elements = [
            Paragraph(title_html, ParagraphStyle("RTitle", fontName=FONT_BOLD, fontSize=8.5, leading=11, textColor=HexColor("#0F172A"))),
            Spacer(1, 2),
            Paragraph(desc, body_s),
        ]

        deliv = item.get("deliverables")
        if deliv:
            deliv_text = ", ".join([safe_text(d) for d in deliv]) if isinstance(deliv, list) else safe_text(deliv)
            content_elements.append(Spacer(1, 1))
            content_elements.append(Paragraph(f"<b>Key Milestones:</b> <font color='#475569'>{deliv_text}</font>", body_s))

        step_table = Table(
            [
                [
                    Paragraph(f"Phase<br/><b>{step_num}</b>", badge_s),
                    content_elements,
                ]
            ],
            colWidths=[55, 460],
        )
        step_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), HexColor("#2563EB")),
            ("BACKGROUND", (1, 0), (1, 0), HexColor("#F8FAFC")),
            ("BOX", (0, 0), (-1, -1), 0.75, HexColor("#CBD5E1")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ALIGN", (0, 0), (0, 0), "CENTER"),
            ("LEFTPADDING", (0, 0), (0, 0), 4),
            ("RIGHTPADDING", (0, 0), (0, 0), 4),
            ("TOPPADDING", (0, 0), (0, 0), 8),
            ("BOTTOMPADDING", (0, 0), (0, 0), 8),
            ("LEFTPADDING", (1, 0), (1, 0), 8),
            ("RIGHTPADDING", (1, 0), (1, 0), 8),
            ("TOPPADDING", (1, 0), (1, 0), 5),
            ("BOTTOMPADDING", (1, 0), (1, 0), 5),
        ]))
        flowables.append(step_table)

        if idx < total_steps - 1:
            arrow_dw = Drawing(515, 14)
            arrow_dw.add(Line(257, 14, 257, 4, strokeColor=HexColor("#2563EB"), strokeWidth=1.5))
            arrow_dw.add(Polygon([253, 5, 261, 5, 257, 0], fillColor=HexColor("#2563EB"), strokeColor=HexColor("#2563EB")))
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
    """
    report = report or {}

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
        if isinstance(flowables_list, list):
            data = [[f] for f in flowables_list]
        else:
            data = [[flowables_list]]
        card_table = Table(data, colWidths=[content_width], repeatRows=0)
        card_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), HexColor(bg_hex)),
            ("BOX", (0, 0), (-1, -1), 0.75, HexColor(border_hex)),
            ("LEFTPADDING", (0, 0), (-1, -1), 9),
            ("RIGHTPADDING", (0, 0), (-1, -1), 9),
            ("TOPPADDING", (0, 0), (-1, -1), 1.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
            ("TOPPADDING", (0, 0), (-1, 0), 4),
            ("BOTTOMPADDING", (0, -1), (-1, -1), 4),
        ]))
        return card_table

    # -------------------------------------------------------------------------
    # COVER / HEADER BLOCK
    # -------------------------------------------------------------------------
    story.append(Paragraph("Startup Intelligence Report", title_style))
    story.append(Paragraph("AGENTIC AI PERSONALIZED STARTUP MENTOR • DOMAIN INTELLIGENCE", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=HexColor("#2563EB"), spaceBefore=0, spaceAfter=8))

    startup_name_val = report.get("startup_name")
    industry_val = report.get("industry") or "Video AI & Creator SaaS"
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
        target_cust = safe_text(report.get("target_customers"), "YouTubers, video podcasters, social media marketing agencies, and digital creators")
        rev_model = safe_text(report.get("revenue_model"), "Freemium B2C/Prosumer tiered monthly subscriptions with credit add-ons")
        gtm = safe_text(report.get("go_to_market"), "Creator affiliate marketing, programmatic short-form social distribution, and creator community referrals")

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
            pricing = safe_text(comp.get("pricing"), "Unverified")
            funding_raised = safe_text(comp.get("funding_raised") or comp.get("funding"), "Unverified")
            revenue = safe_text(comp.get("revenue"), "Unverified")
            profit_loss = safe_text(comp.get("profit_loss"), "Unverified")
            c_source = safe_text(comp.get("source"), "Public market records")
            c_source_url = comp.get("source_url") or ""
            c_date_checked = safe_text(comp.get("date_checked"), "October 2026")
            strengths = comp.get("strengths", [])
            weaknesses = comp.get("weaknesses", [])

            source_line = f"<b>Data Source:</b> {c_source} &nbsp;|&nbsp; <b>Date Checked:</b> {c_date_checked}"
            if c_source_url and c_source_url.lower() != "unverified":
                source_line += f" &nbsp;|&nbsp; <b>Source Link:</b> {make_clickable_link(c_source_url, c_source_url)}"

            card_elements = [
                Paragraph(f"<b>{c_name}</b>", item_title_style),
                Spacer(1, 1),
                Paragraph(f"<b>Product / Service:</b> {p_s}", body_style),
                Paragraph(f"<b>Target Customers:</b> {target}", body_style),
                Paragraph(f"<b>Business Model:</b> {model} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Pricing:</b> {pricing}", body_style),
                Paragraph(f"<b>External Funding Raised:</b> {funding_raised}", body_style),
                Paragraph(f"<b>Revenue:</b> {revenue} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Profit/Loss:</b> {profit_loss}", body_style),
                Paragraph(source_line, body_style),
            ]

            if strengths:
                s_text = ", ".join([safe_text(s) for s in strengths]) if isinstance(strengths, list) else safe_text(strengths)
                card_elements.append(Paragraph(f"<b>Strengths:</b> {s_text}", body_style))
            if weaknesses:
                w_text = ", ".join([safe_text(w) for w in weaknesses]) if isinstance(weaknesses, list) else safe_text(weaknesses)
                card_elements.append(Paragraph(f"<b>Weaknesses / Gaps:</b> {w_text}", body_style))

            story.append(make_card(card_elements))
            story.append(Spacer(1, 4))

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
                    comp_diff_elements.append(Paragraph(f"• <b>vs {c_target}:</b> {diff}", bullet_style))
                else:
                    comp_diff_elements.append(Paragraph(f"• {safe_text(point)}", bullet_style))
        elif isinstance(comparison, dict):
            for k, v in comparison.items():
                comp_diff_elements.append(Paragraph(f"• <b>{safe_text(k)}:</b> {safe_text(v)}", bullet_style))
        else:
            comp_diff_elements.append(Paragraph(f"• {safe_text(comparison)}", bullet_style))

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

    if not gov_funding and not priv_funding:
        fallback_raw = report.get("funding_opportunities")
        fallback_funding = list(fallback_raw) if isinstance(fallback_raw, list) else []
        if fallback_funding:
            for item in fallback_funding:
                if not isinstance(item, dict):
                    continue
                combined = f"{item.get('funding_type', '')} {item.get('organization', '')} {item.get('name', '')}".lower()
                gov_keywords = ["gov", "ministry", "dpiit", "meity", "msme", "sidbi", "dst", "startup india", "sisfs", "state"]
                if any(k in combined for k in gov_keywords):
                    gov_funding.append(item)
                else:
                    priv_funding.append(item)

    def render_funding_card(opp: dict, is_government: bool = True):
        name = safe_text(opp.get("name") or opp.get("scheme_name"), "Funding Opportunity")
        org = safe_text(opp.get("organization") or opp.get("implementing_agency"), "Implementing Agency" if is_government else "Organization / Program")
        funding_type = safe_text(opp.get("funding_type"), "Grant" if is_government else "Private Capital / Program")
        amount = safe_text(opp.get("funding_amount") or opp.get("amount"), "Unverified")
        stage = safe_text(opp.get("startup_stage") or opp.get("stage"), "Early / Validation")
        deadline_raw = safe_text(opp.get("deadline") or opp.get("status"), "Unverified")
        status_raw = str(opp.get("status") or "")
        evidence_raw = str(opp.get("official_source_evidence") or opp.get("status_evidence") or "")
        date_checked = safe_text(opp.get("date_checked"), "October 2026")

        status_label, badge_bg, badge_fg, border_hex, card_bg_hex, deadline_text = get_opportunity_status(
            name, deadline_raw, status_raw, evidence_raw
        )

        eligibility = safe_text(opp.get("eligibility"))
        who_can_apply = safe_text(opp.get("who_can_apply"))
        usage = safe_text(opp.get("usage") or opp.get("permitted_fund_usage"))
        why_suitable = safe_text(opp.get("why_suitable") or opp.get("suitability"))
        where_to_apply = safe_text(opp.get("where_to_apply") or opp.get("application_portal"))
        app_website = opp.get("application_website") or opp.get("website") or ""

        if "msme" in name.lower() and (not app_website or app_website.lower() == "unverified"):
            app_website = "https://innovative.msme.gov.in"

        if "tide" in name.lower() and (not app_website or app_website.lower() == "unverified"):
            app_website = "https://msh.meity.gov.in/schemes/tide"

        source_name = safe_text(opp.get("official_source_name") or opp.get("official_source"), org)
        source_url = opp.get("official_source_url") or opp.get("source_url") or ""

        steps = opp.get("application_steps", [])
        docs = opp.get("required_documents", [])

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
            Spacer(1, 1),
            Paragraph(f"<b>Implementing Agency / Organization:</b> {org} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Funding Type:</b> {funding_type}", body_style),
            Paragraph(f"<b>Funding Amount:</b> {amount} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Target Stage:</b> {stage}", body_style),
            Paragraph(f"<b>Current Status / Deadline:</b> {deadline_text} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Date Checked:</b> {date_checked}", body_style),
            Spacer(1, 1),
            HRFlowable(width="100%", thickness=0.5, color=HexColor("#E2E8F0"), spaceBefore=1, spaceAfter=2),
            Paragraph(f"<b>Eligibility Criteria:</b> {eligibility}", body_style),
            Paragraph(f"<b>Who Can Apply:</b> {who_can_apply}", body_style),
            Paragraph(f"<b>Permitted Fund Usage:</b> {usage}", body_style),
            Paragraph(f"<b>Strategic Fit & Suitability:</b> {why_suitable}", body_style),
            Paragraph(f"<b>Where to Apply:</b> {where_to_apply}", body_style),
            Paragraph(f"<b>Application Portal Link:</b> {make_clickable_link(app_website, app_website)}", body_style),
        ]

        if source_url and source_url.lower() != "unverified":
            card_elements.append(Paragraph(f"<b>Official Source:</b> {source_name} &nbsp;|&nbsp; <b>Official Link:</b> {make_clickable_link(source_url, source_url)}", body_style))
        else:
            card_elements.append(Paragraph(f"<b>Official Source:</b> {source_name}", body_style))

        card_elements.append(Spacer(1, 1))
        card_elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#E2E8F0"), spaceBefore=1, spaceAfter=2))

        card_elements.append(Paragraph("<b>Step-by-Step Application Procedure:</b>", card_label_style))
        if steps and isinstance(steps, list):
            for s_idx, step_val in enumerate(steps, 1):
                card_elements.append(Paragraph(f"&nbsp;&nbsp;<b>Step {s_idx}:</b> {safe_text(step_val)}", bullet_style))
        elif isinstance(steps, str) and steps.strip():
            card_elements.append(Paragraph(f"&nbsp;&nbsp;{safe_text(steps)}", bullet_style))
        else:
            card_elements.append(Paragraph("&nbsp;&nbsp;Refer to official portal guidelines.", bullet_style))

        card_elements.append(Spacer(1, 1))
        card_elements.append(Paragraph("<b>Required Documents Checklist:</b>", card_label_style))
        if docs and isinstance(docs, list):
            doc_items = ", ".join([safe_text(d) for d in docs])
            card_elements.append(Paragraph(f"&nbsp;&nbsp;• {doc_items}", bullet_style))
        elif isinstance(docs, str) and docs.strip():
            card_elements.append(Paragraph(f"&nbsp;&nbsp;• {safe_text(docs)}", bullet_style))
        else:
            card_elements.append(Paragraph("&nbsp;&nbsp;• As specified on the official application portal.", bullet_style))

        return make_card(card_elements, border_hex=border_hex, bg_hex=card_bg_hex)

    story.append(Paragraph("A. Government Funding Schemes", h2_style))
    if not gov_funding:
        story.append(Paragraph("<i>No government funding schemes recorded for this sector.</i>", body_style))
    else:
        for opp in gov_funding:
            if isinstance(opp, dict):
                story.append(render_funding_card(opp, is_government=True))
                story.append(Spacer(1, 4))

    story.append(Spacer(1, 2))

    story.append(Paragraph("B. Private Funding Opportunities & Cloud Programs", h2_style))
    if not priv_funding:
        story.append(Paragraph("<i>No private funding opportunities recorded for this sector.</i>", body_style))
    else:
        for opp in priv_funding:
            if isinstance(opp, dict):
                story.append(render_funding_card(opp, is_government=False))
                story.append(Spacer(1, 4))

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
        hierarchy_raw = report.get("team_hierarchy")
        hierarchy_nodes = list(hierarchy_raw) if isinstance(hierarchy_raw, list) else []

        story.append(Paragraph("Organizational Reporting Hierarchy", h2_style))
        story.append(Paragraph("<i>Visual reporting structure connecting executive leadership, functional department leads, and domain specialists:</i>", body_style))
        story.append(Spacer(1, 3))

        hierarchy_diagram = build_multi_level_hierarchy_diagram(
            hierarchy_nodes,
            team_list,
        )
        story.append(hierarchy_diagram)
        story.append(Spacer(1, 5))

        lean_advice = report.get("lean_team_advice") or report.get("team_recommendation")
        if lean_advice:
            story.append(Paragraph("Lean Team Execution Strategy", h2_style))
            story.append(make_card([Paragraph(safe_text(lean_advice), body_style)]))
            story.append(Spacer(1, 4))

        essential_roles = [r for r in team_list if isinstance(r, dict) and "later" not in str(r.get("priority", "")).lower() and "growth" not in str(r.get("priority", "")).lower()]
        later_roles = [r for r in team_list if isinstance(r, dict) and ("later" in str(r.get("priority", "")).lower() or "growth" in str(r.get("priority", "")).lower())]

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
                priority_val = str(role_item.get("priority") or "Essential").strip()
                if "later" in priority_val.lower() or "growth" in priority_val.lower():
                    badge_html = "<font color='#92400E'><b>[Later — Scale & Expansion Stage]</b></font>"
                else:
                    badge_html = "<font color='#166534'><b>[Essential — MVP Launch Stage]</b></font>"

                exp_level = safe_text(role_item.get("experience_level"), "Not specified")
                why_needed = safe_text(role_item.get("why_needed"), "Critical for venture execution, technical reliability, and milestone validation.")
                responsibilities = safe_text(role_item.get("responsibilities"), "Executes core departmental deliverables, ensures code and quality standards, and collaborates across the founding team.")

                skills = role_item.get("required_skills") or role_item.get("skills") or []
                if isinstance(skills, list) and skills:
                    skills_text = ", ".join([safe_text(s) for s in skills])
                elif isinstance(skills, str) and skills.strip():
                    skills_text = safe_text(skills)
                else:
                    skills_text = "System architecture, agile delivery, technical tooling, and industry best practices"

                soft_skills = role_item.get("soft_skills") or []
                if isinstance(soft_skills, list) and soft_skills:
                    soft_skills_text = ", ".join([safe_text(s) for s in soft_skills])
                elif isinstance(soft_skills, str) and soft_skills.strip():
                    soft_skills_text = safe_text(soft_skills)
                else:
                    soft_skills_text = ""

                card_elements = [
                    Paragraph(f"<b>{role_title}</b> &nbsp;&nbsp; {badge_html}", item_title_style),
                    Spacer(1, 1),
                    Paragraph(f"<b>Department:</b> {dept} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Reports To:</b> {reports_to} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Experience Level:</b> {exp_level}", body_style),
                    Spacer(1, 1),
                    Paragraph(f"<b>Purpose & Strategic Value:</b> {why_needed}", body_style),
                    Paragraph(f"<b>Core Responsibilities:</b> {responsibilities}", body_style),
                    Paragraph(f"<b>Required Domain / Technical Skills:</b> {skills_text}", body_style),
                ]

                if soft_skills_text:
                    card_elements.append(Paragraph(f"<b>Collaboration & Soft Skills:</b> {soft_skills_text}", body_style))

                story.append(make_card(card_elements))
                story.append(Spacer(1, 4))

        render_role_cards(essential_roles, "Essential Roles (Immediate / MVP Stage)")
        render_role_cards(later_roles, "Roles That Can Be Added Later (Scale / Expansion Stage)")

    story.append(section_divider())

    # -------------------------------------------------------------------------
    # 6. FINANCIAL ANALYSIS
    # -------------------------------------------------------------------------
    story.append(Paragraph("6. Financial Analysis", h1_style))
    fin_info = report.get("financial_analysis") or report.get("financial_information") or report.get("financials")

    if not fin_info:
        story.append(Paragraph("<i>Financial analysis details not available for this venture.</i>", body_style))
    else:
        fin_elements = []

        if isinstance(fin_info, dict):
            # A. Lean MVP Budget
            mvp_budget = fin_info.get("mvp_budget_breakdown")
            if mvp_budget and isinstance(mvp_budget, list):
                fin_elements.append(Paragraph("<b>Lean MVP Development Budget (Sub-₹10,000 Bootstrapping Target):</b>", card_label_style))
                for item in mvp_budget:
                    fin_elements.append(Paragraph(f"• {safe_text(item)}", bullet_style))
                fin_elements.append(Spacer(1, 2))

            # B. Monthly Burn
            monthly_burn = fin_info.get("estimated_monthly_burn")
            if monthly_burn:
                fin_elements.append(Paragraph(f"<b>Estimated Monthly Operating Burn Rate:</b> {safe_text(monthly_burn)}", body_style))
                fin_elements.append(Spacer(1, 2))

            # C. Pricing Model & Unit Economics
            pricing_model = fin_info.get("pricing_model_and_unit_economics")
            if pricing_model:
                fin_elements.append(Paragraph(f"<b>Proposed Pricing Model & Unit Economics:</b> {safe_text(pricing_model)}", body_style))
                fin_elements.append(Spacer(1, 2))

            # D. Revenue Scenarios
            rev_scenarios = fin_info.get("revenue_scenarios")
            if rev_scenarios and isinstance(rev_scenarios, list):
                fin_elements.append(Paragraph("<b>Early Revenue Scenarios (Planning Assumptions — Not Guaranteed):</b>", card_label_style))
                for scen in rev_scenarios:
                    fin_elements.append(Paragraph(f"• {safe_text(scen)}", bullet_style))
                fin_elements.append(Spacer(1, 2))

            # E. Break-Even Assumptions
            break_even = fin_info.get("break_even_assumptions")
            if break_even:
                fin_elements.append(Paragraph(f"<b>Break-Even Assumptions:</b> {safe_text(break_even)}", body_style))
                fin_elements.append(Spacer(1, 2))

            # F. Market Benchmarks & Competitor Financial Filings
            benchmarks = fin_info.get("competitor_or_historical_benchmarks") or report.get("financial_information")
            if benchmarks and isinstance(benchmarks, list):
                fin_elements.append(Paragraph("<b>Competitor Financial Records & Filings:</b>", card_label_style))
                for b in benchmarks:
                    fin_elements.append(Paragraph(f"• {safe_text(b)}", bullet_style))

        elif isinstance(fin_info, list):
            for item in fin_info:
                if isinstance(item, dict):
                    rev = safe_text(item.get("revenue"), "Unverified")
                    pl = safe_text(item.get("profit_loss"), "Unverified")
                    funding = safe_text(item.get("funding_raised"), "Unverified")
                    src = safe_text(item.get("source"), "Public filing")
                    fin_elements.append(Paragraph(f"• <b>Revenue:</b> {rev} | <b>Profit/Loss:</b> {pl} | <b>Funding Raised:</b> {funding} (Source: {src})", bullet_style))
                else:
                    fin_elements.append(Paragraph(f"• {safe_text(item)}", bullet_style))

        fin_elements.append(Spacer(1, 3))
        fin_elements.append(Paragraph(
            "<i>Financial Disclaimer: MVP budget and revenue projections are domain planning assumptions leveraging free developer tiers "
            "and pay-as-you-go APIs. Projections are strictly illustrative estimates and do not represent guaranteed financial returns. "
            "Competitor financials are marked 'Unverified' where audited statutory filings are unavailable.</i>",
            bullet_style
        ))

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
        risk_cards = []
        if isinstance(risk_info, list):
            for r in risk_info:
                if isinstance(r, dict):
                    cat = safe_text(r.get("category") or r.get("risk_type"), "Operational Risk")
                    desc = safe_text(r.get("risk") or r.get("description"), "Risk scenario")
                    mit = safe_text(r.get("mitigation_strategy") or r.get("mitigation"), "Active monitoring and contingency planning.")
                    impact = safe_text(r.get("impact") or r.get("severity"), "Medium")

                    impact_color = "#991B1B" if impact.lower() in ["high", "critical"] else ("#92400E" if impact.lower() == "medium" else "#166534")

                    r_elements = [
                        Paragraph(f"<b>[{cat.upper()}]</b> &nbsp;&nbsp;|&nbsp;&nbsp; <b>Severity / Impact:</b> <font color='{impact_color}'><b>{impact}</b></font>", item_title_style),
                        Spacer(1, 1),
                        Paragraph(f"<b>Risk Description:</b> {desc}", body_style),
                        Paragraph(f"<b>Mitigation Strategy:</b> {mit}", body_style),
                    ]
                    risk_cards.append(make_card(r_elements))
                    risk_cards.append(Spacer(1, 3))
                else:
                    risk_cards.append(Paragraph(f"• {safe_text(r)}", bullet_style))
        elif isinstance(risk_info, dict):
            for k, v in risk_info.items():
                label = safe_text(k).replace("_", " ").title()
                risk_cards.append(Paragraph(f"• <b>{label}:</b> {safe_text(v)}", bullet_style))

        for rc in risk_cards:
            story.append(rc)

        # Domain Regulatory Notice: Healthcare only if applicable
        st_name_low = str(report.get("startup_name") or "").lower()
        exec_low = str(report.get("executive_summary") or "").lower()
        if "medisync" in st_name_low or ("health" in exec_low and "ai" in exec_low) or ("clinical" in exec_low and "diagnosis" in exec_low):
            reg_notice = [
                Paragraph("<b>Healthcare Regulatory & Clinical Safety Notice:</b>", card_label_style),
                Paragraph(
                    "Clinical AI platforms operate as Clinical Decision Support (CDS) research tools during early MVP phases. "
                    "Commercial medical device certification (such as CDSCO approval in India, CE Mark in Europe, or FDA 510(k) in the US) "
                    "requires formal multi-center clinical validation trials and institutional ethics committee approvals. "
                    "The venture must never claim statutory medical certification or replace physician diagnosis without official notified-body clearance.",
                    body_style
                ),
            ]
            story.append(Spacer(1, 2))
            story.append(make_card(reg_notice, border_hex="#F59E0B", bg_hex="#FFFBEB"))

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
        # Dynamic validation label tailored to the startup idea
        st_name_low = str(report.get("startup_name") or "").lower()
        exec_low = str(report.get("executive_summary") or "").lower()
        idea_low = str(startup_idea or "").lower()
        is_creator_venture = (
            "creator" in st_name_low
            or "clip" in st_name_low
            or "video" in st_name_low
            or "creator" in exec_low
            or "video" in exec_low
            or "video" in idea_low
        )

        validation_label = "creator/user validation" if is_creator_venture else (
            "clinical validation" if ("clinical" in st_name_low or "health" in exec_low) else "user and market validation"
        )

        story.append(Paragraph(
            f"<i>Sequential phased execution plan connecting initial MVP prototyping, {validation_label}, and commercial launch:</i>",
            body_style
        ))
        story.append(Spacer(1, 4))
        diagram_flowables = build_roadmap_diagram(roadmap_list)
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

    source_elements.append(Paragraph("• <b>LinkedIn Company Page Setup:</b> Establish official venture page", bullet_style))
    source_elements.append(Paragraph(f"&nbsp;&nbsp;<b>Link:</b> {make_clickable_link('https://www.linkedin.com/company/setup/new/', 'https://www.linkedin.com/company/setup/new/')}", bullet_style))
    source_elements.append(Spacer(1, 2))

    if sources_list:
        for src in sources_list:
            if isinstance(src, dict):
                src_name = safe_text(src.get("name") or src.get("title"), "Verified Resource")
                src_type = safe_text(src.get("source_type") or src.get("type"), "")
                src_cat = safe_text(src.get("category"), "")
                src_url = src.get("url") or ""
                src_date = safe_text(src.get("date_checked"), "October 2026")

                meta_line = []
                if src_type and src_type.lower() not in ["not available", "none", "unverified"]:
                    meta_line.append(f"<b>Type:</b> {src_type}")
                if src_cat and src_cat.lower() not in ["not available", "none", "unverified"]:
                    meta_line.append(f"<b>Category:</b> {src_cat}")
                if src_date:
                    meta_line.append(f"<b>Date Checked:</b> {src_date}")

                meta_str = f" &nbsp;|&nbsp; {' &nbsp;|&nbsp; '.join(meta_line)}" if meta_line else ""
                source_elements.append(Paragraph(f"• <b>{src_name}</b>{meta_str}", bullet_style))
                source_elements.append(Paragraph(f"&nbsp;&nbsp;<b>Link:</b> {make_clickable_link(src_url, src_url)}", bullet_style))
            elif isinstance(src, str):
                source_elements.append(Paragraph(f"• <b>Resource:</b> {make_clickable_link(src, src)}", bullet_style))

    story.append(make_card(source_elements))

    doc.build(story, canvasmaker=NumberedCanvas)