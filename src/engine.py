"""
OpenMV Datasheet PDF Generation Engine.

Generates professional datasheets from YAML product data files using ReportLab.
"""

import os
from datetime import date
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image,
    PageBreak, KeepTogether, HRFlowable,
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib.colors import white
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate, Frame
from reportlab.platypus.flowables import Flowable

from . import styles as S


class HeaderFooter:
    """Draws consistent header and footer on every page."""

    def __init__(self, product_name, modified_date, version, logo_path=None):
        self.product_name = product_name
        self.modified_date = modified_date
        self.version = version
        self.logo_path = logo_path

    def _draw_footer(self, canvas, doc, width):
        canvas.setFillColor(S.MEDIUM_GRAY)
        canvas.setFont("Helvetica", 7.5)
        canvas.drawString(S.MARGIN_LEFT, 28, f"{doc.page}")
        canvas.drawCentredString(width / 2, 28,
                                 f"OpenMV\u00AE {self.product_name}")
        canvas.drawRightString(width - S.MARGIN_RIGHT, 28,
                               f"{self.version}  \u2022  Modified {self.modified_date}")
        canvas.setStrokeColor(S.TABLE_BORDER)
        canvas.setLineWidth(0.5)
        canvas.line(S.MARGIN_LEFT, 42, width - S.MARGIN_RIGHT, 42)

    def __call__(self, canvas, doc):
        canvas.saveState()
        width, height = letter

        # Header: logo left, product name + "Datasheet" right, thin line below
        header_y = height - 32
        if self.logo_path and os.path.exists(self.logo_path):
            canvas.drawImage(self.logo_path, S.MARGIN_LEFT, header_y - 2,
                             width=72, height=24, preserveAspectRatio=True, mask="auto")
        canvas.setFillColor(S.OPENMV_DARK)
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawRightString(width - S.MARGIN_RIGHT, header_y + 4,
                               f"OpenMV\u00AE {self.product_name}  \u2014  Datasheet")
        # Header line
        canvas.setStrokeColor(S.TABLE_BORDER)
        canvas.setLineWidth(0.5)
        canvas.line(S.MARGIN_LEFT, header_y - 6, width - S.MARGIN_RIGHT, header_y - 6)

        self._draw_footer(canvas, doc, width)
        canvas.restoreState()


class CoverHeaderFooter(HeaderFooter):
    """Header/footer for the cover page (footer only, no header bar)."""

    def __call__(self, canvas, doc):
        canvas.saveState()
        width, height = letter
        self._draw_footer(canvas, doc, width)
        canvas.restoreState()


class TealLine(Flowable):
    """A horizontal teal accent line."""

    def __init__(self, width, thickness=2):
        super().__init__()
        self.line_width = width
        self.thickness = thickness
        self.height = thickness + 4

    def wrap(self, availWidth, availHeight):
        return self.line_width, self.height

    def draw(self):
        self.canv.setStrokeColor(S.OPENMV_TEAL)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, self.height / 2, self.line_width, self.height / 2)


class DatasheetBuilder:
    """Builds a complete datasheet PDF from structured product data."""

    def __init__(self, product_data, media_dir="media", output_dir="output"):
        self.data = product_data
        self.media_dir = media_dir
        self.output_dir = output_dir
        self.elements = []
        self.toc_entries = []
        self.section_counter = 0
        self.subsection_counters = {}

    def _resolve_image(self, path):
        """Resolve an image path relative to media_dir or absolute."""
        if os.path.isabs(path):
            return path
        full = os.path.join(self.media_dir, path)
        if os.path.exists(full):
            return full
        return path

    def _make_table(self, headers, rows, col_widths=None, notes=None):
        """Create a styled table with header row and optional notes."""
        header_cells = [Paragraph(h, S.STYLE_TABLE_HEADER) for h in headers]
        table_data = [header_cells]

        for row in rows:
            table_data.append([
                Paragraph(str(cell), S.STYLE_TABLE_BODY) if not isinstance(cell, Paragraph) else cell
                for cell in row
            ])

        if col_widths is None:
            col_widths = [S.CONTENT_WIDTH / len(headers)] * len(headers)

        t = Table(table_data, colWidths=col_widths, repeatRows=1)

        style_commands = [
            ("BACKGROUND", (0, 0), (-1, 0), S.TABLE_HEADER_BG),
            ("TEXTCOLOR", (0, 0), (-1, 0), S.TABLE_HEADER_TEXT),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), S.TABLE_HEADER_SIZE),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
            ("TOPPADDING", (0, 0), (-1, 0), 6),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), S.TABLE_BODY_SIZE),
            ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
            ("TOPPADDING", (0, 1), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("GRID", (0, 0), (-1, -1), 0.5, S.TABLE_BORDER),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]

        # Alternate row colors
        for i in range(1, len(table_data)):
            if i % 2 == 0:
                style_commands.append(
                    ("BACKGROUND", (0, i), (-1, i), S.TABLE_ALT_ROW)
                )

        t.setStyle(TableStyle(style_commands))

        elements = [t]
        if notes:
            elements.append(Spacer(1, 4))
            for note in notes:
                elements.append(Paragraph(note, S.STYLE_NOTE))

        return elements

    def _make_component_table(self, components):
        """Create a Component / Details style table from a list of dicts."""
        rows = []
        for comp in components:
            name = Paragraph(f"<b>{comp['name']}</b>", S.STYLE_TABLE_BODY)
            details = comp.get("details", "")
            if isinstance(details, list):
                details = "<br/>".join(str(d) for d in details)
            detail_cell = Paragraph(str(details), S.STYLE_TABLE_BODY)
            rows.append([name, detail_cell])

        return self._make_table(
            ["Component", "Details"],
            rows,
            col_widths=[S.CONTENT_WIDTH * 0.28, S.CONTENT_WIDTH * 0.72],
            notes=None,
        )

    def _add_section(self, title):
        """Add a numbered top-level section heading."""
        self.section_counter += 1
        num = self.section_counter
        self.subsection_counters[num] = 0
        heading = f"{num}  {title}"
        self.toc_entries.append((1, title, num))
        self.elements.append(Paragraph(heading, S.STYLE_H1))
        self.elements.append(TealLine(S.CONTENT_WIDTH, thickness=1.5))
        self.elements.append(Spacer(1, 4))
        return num

    def _add_subsection(self, title, parent_num=None):
        """Add a numbered subsection heading."""
        if parent_num is None:
            parent_num = self.section_counter
        self.subsection_counters[parent_num] = self.subsection_counters.get(parent_num, 0) + 1
        sub_num = self.subsection_counters[parent_num]
        heading = f"{parent_num}.{sub_num}  {title}"
        self.toc_entries.append((2, title, f"{parent_num}.{sub_num}"))
        self.elements.append(Paragraph(heading, S.STYLE_H2))
        self.elements.append(Spacer(1, 2))
        return f"{parent_num}.{sub_num}"

    def _start_group(self):
        """Mark the start of a group of elements to keep together."""
        return len(self.elements)

    def _end_group(self, start_idx):
        """Wrap elements from start_idx to end in KeepTogether."""
        group = self.elements[start_idx:]
        if group:
            del self.elements[start_idx:]
            self.elements.append(KeepTogether(group))

    def build_cover_page(self):
        """Build the cover / first page matching the RT1062 reference layout."""
        meta = self.data["meta"]
        product_name = meta["product_name"]

        # Row 1: Logo (left) | Product name (right) — on the same line
        logo_cell = Spacer(1, 1)
        logo_path = self._resolve_image("logos/openmv-logo/logo.png")
        if os.path.exists(logo_path):
            logo_cell = Image(logo_path, width=1.4 * inch, height=0.47 * inch,
                              kind="proportional")

        name_right = Paragraph(
            f"OpenMV\u00AE {product_name}",
            S.STYLE_COVER_PRODUCT_NAME,
        )

        banner = Table(
            [[logo_cell, name_right]],
            colWidths=[S.CONTENT_WIDTH * 0.50, S.CONTENT_WIDTH * 0.50],
        )
        banner.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (1, 0), (1, 0), "RIGHT"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))
        self.elements.append(banner)

        # Thin horizontal rule under the banner
        self.elements.append(HRFlowable(
            width="100%", thickness=0.75, color=S.OPENMV_DARK,
            spaceAfter=8, spaceBefore=4,
        ))

        # Right-aligned "Datasheet" and SKU
        self.elements.append(Paragraph("Datasheet", S.STYLE_COVER_DATASHEET_LABEL))
        if "sku" in meta:
            self.elements.append(Paragraph(
                f"SKU: {meta['sku']}", S.STYLE_COVER_SKU_RIGHT,
            ))

        self.elements.append(Spacer(1, 10))

        # Description with product image floated right
        # Build as a two-column table: description left, image right
        desc_content = []
        if "description" in self.data:
            desc_content.append(Paragraph("<b>Description</b>", S.STYLE_H2))
            desc_content.append(Spacer(1, 4))
            desc = self.data["description"]
            if isinstance(desc, list):
                for p in desc:
                    desc_content.append(Paragraph(p, S.STYLE_COVER_DESCRIPTION))
            else:
                desc_content.append(Paragraph(desc, S.STYLE_COVER_DESCRIPTION))

        img_cell = [Spacer(1, 1)]
        if "cover_image" in meta:
            img_path = self._resolve_image(meta["cover_image"])
            if os.path.exists(img_path):
                img_cell = [Image(img_path, width=2.4 * inch, height=2.4 * inch,
                                  kind="proportional")]

        desc_table = Table(
            [[desc_content, img_cell]],
            colWidths=[S.CONTENT_WIDTH * 0.58, S.CONTENT_WIDTH * 0.42],
        )
        desc_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (0, 0), "TOP"),
            ("VALIGN", (1, 0), (1, 0), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (0, 0), 8),
            ("RIGHTPADDING", (1, 0), (1, 0), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))
        self.elements.append(desc_table)
        self.elements.append(Spacer(1, 8))

        # Target areas — full width below
        if "target_areas" in self.data:
            self.elements.append(Paragraph("<b>Target Areas</b>", S.STYLE_H2))
            self.elements.append(Spacer(1, 4))
            self.elements.append(Paragraph(self.data["target_areas"], S.STYLE_COVER_DESCRIPTION))

        # Feature highlights
        if "features" in self.data:
            self.elements.append(Spacer(1, 6))
            self.elements.append(Paragraph("<b>Key Features</b>", S.STYLE_H2))
            self.elements.append(Spacer(1, 4))
            for feat in self.data["features"]:
                if isinstance(feat, dict):
                    label = feat.get("label", "")
                    detail = feat.get("detail", "")
                    text = f"<b>{label}</b> \u2014 {detail}" if detail else f"<b>{label}</b>"
                else:
                    text = str(feat)
                self.elements.append(
                    Paragraph(text, S.STYLE_FEATURE_BULLET, bulletText="\u2022")
                )

    def build_toc_page(self):
        """Build the table of contents page (placeholder, filled after build)."""
        self.elements.append(PageBreak())
        self.elements.append(Paragraph("Contents", S.STYLE_H1))
        self.elements.append(TealLine(S.CONTENT_WIDTH, thickness=1.5))
        self.elements.append(Spacer(1, 12))
        # TOC entries are added in finalize step
        self._toc_insert_index = len(self.elements)
        # Force page break after TOC so content doesn't creep onto TOC page
        self.elements.append(PageBreak())

    def build_features_section(self):
        """Build Section 1: Features and System Components."""
        if "system_components" not in self.data:
            return

        section_title = self.data.get("system_components_title", "Features and System Components")
        sec_num = self._add_section(section_title)

        for subsection in self.data["system_components"]:
            g = self._start_group()
            title = subsection["title"]
            self._add_subsection(title, sec_num)

            if "components" in subsection:
                elems = self._make_component_table(subsection["components"])
                self.elements.extend(elems)
                self.elements.append(Spacer(1, 6))

            if "text" in subsection:
                self.elements.append(Paragraph(subsection["text"], S.STYLE_BODY))

            if "notes" in subsection:
                for note in subsection["notes"]:
                    self.elements.append(Paragraph(note, S.STYLE_NOTE))
            self._end_group(g)

    def build_ratings_section(self):
        """Build Section 2: Ratings."""
        if "ratings" not in self.data:
            return

        sec_num = self._add_section("Ratings")

        for subsection in self.data["ratings"]:
            g = self._start_group()
            title = subsection["title"]
            self._add_subsection(title, sec_num)

            headers = subsection.get("headers", ["Symbol", "Description", "Min", "Typ", "Max", "Unit"])
            rows = subsection.get("rows", [])
            notes = subsection.get("notes", None)

            num_cols = len(headers)
            # Smart column widths for ratings tables
            if num_cols == 6:
                col_widths = [
                    S.CONTENT_WIDTH * 0.10,
                    S.CONTENT_WIDTH * 0.38,
                    S.CONTENT_WIDTH * 0.12,
                    S.CONTENT_WIDTH * 0.12,
                    S.CONTENT_WIDTH * 0.12,
                    S.CONTENT_WIDTH * 0.16,
                ]
            elif num_cols == 7:
                col_widths = [
                    S.CONTENT_WIDTH * 0.10,
                    S.CONTENT_WIDTH * 0.28,
                    S.CONTENT_WIDTH * 0.10,
                    S.CONTENT_WIDTH * 0.10,
                    S.CONTENT_WIDTH * 0.10,
                    S.CONTENT_WIDTH * 0.10,
                    S.CONTENT_WIDTH * 0.22,
                ]
            else:
                col_widths = None

            elems = self._make_table(headers, rows, col_widths, notes)
            self.elements.extend(elems)
            self.elements.append(Spacer(1, 6))
            self._end_group(g)

    def build_connector_section(self):
        """Build Section 3: Connector Overview / Pinout."""
        if "connectors" not in self.data:
            return

        sec_num = self._add_section("Connector Overview")

        # Pinout image
        if "pinout_image" in self.data["connectors"]:
            img_path = self._resolve_image(self.data["connectors"]["pinout_image"])
            if os.path.exists(img_path):
                self.elements.append(
                    Image(img_path, width=S.CONTENT_WIDTH, height=4.5 * inch,
                          kind="proportional")
                )
                self.elements.append(Spacer(1, 8))

        for group in self.data["connectors"].get("groups", []):
            g = self._start_group()
            title = group["title"]
            self._add_subsection(title, sec_num)

            headers = group.get("headers", ["Pin", "Label", "Type", "Notes"])
            rows = group.get("rows", [])
            elems = self._make_table(headers, rows)
            self.elements.extend(elems)
            self.elements.append(Spacer(1, 6))
            self._end_group(g)

        if "summary" in self.data["connectors"]:
            g = self._start_group()
            self._add_subsection("Pin Summary", sec_num)
            summary = self.data["connectors"]["summary"]
            headers = summary.get("headers", ["Category", "Signal/Pin(s)", "Description", "Notes"])
            rows = summary.get("rows", [])
            elems = self._make_table(headers, rows)
            self.elements.extend(elems)
            self.elements.append(Spacer(1, 6))
            self._end_group(g)

    def build_functional_overview_section(self):
        """Build Section 4: Functional Overview."""
        if "functional_overview" not in self.data:
            return

        sec_num = self._add_section("Functional Overview")

        fo = self.data["functional_overview"]

        # Board topology
        if "board_topology" in fo:
            bt = fo["board_topology"]
            self._add_subsection("Board Topology", sec_num)

            if "image" in bt:
                img_path = self._resolve_image(bt["image"])
                if os.path.exists(img_path):
                    self.elements.append(
                        Image(img_path, width=S.CONTENT_WIDTH, height=4 * inch,
                              kind="proportional")
                    )
                    self.elements.append(Spacer(1, 8))

            if "components" in bt:
                headers = ["Ref.", "Description"]
                rows = [[c["ref"], c["description"]] for c in bt["components"]]
                elems = self._make_table(headers, rows,
                                         col_widths=[S.CONTENT_WIDTH * 0.15, S.CONTENT_WIDTH * 0.85])
                self.elements.extend(elems)
                self.elements.append(Spacer(1, 6))

        # Power tree
        if "power_tree" in fo:
            g = self._start_group()
            pt = fo["power_tree"]
            self._add_subsection("Power Tree", sec_num)
            if "image" in pt:
                img_path = self._resolve_image(pt["image"])
                if os.path.exists(img_path):
                    self.elements.append(
                        Image(img_path, width=S.CONTENT_WIDTH, height=3 * inch,
                              kind="proportional")
                    )
                    self.elements.append(Spacer(1, 8))
            if "text" in pt:
                self.elements.append(Paragraph(pt["text"], S.STYLE_BODY))
            self._end_group(g)

    def build_mechanical_section(self):
        """Build Section: Mechanical Information."""
        if "mechanical" not in self.data:
            return

        g = self._start_group()
        sec_num = self._add_section("Mechanical Information")
        mech = self.data["mechanical"]

        if "dimensions_image" in mech:
            img_path = self._resolve_image(mech["dimensions_image"])
            if os.path.exists(img_path):
                self.elements.append(
                    Image(img_path, width=S.CONTENT_WIDTH * 0.7, height=3 * inch,
                          kind="proportional")
                )
                self.elements.append(Spacer(1, 8))

        if "specs" in mech:
            headers = ["Dimension", "Value"]
            rows = [[s["dimension"], s["value"]] for s in mech["specs"]]
            elems = self._make_table(headers, rows,
                                     col_widths=[S.CONTENT_WIDTH * 0.35, S.CONTENT_WIDTH * 0.65])
            self.elements.extend(elems)
            self.elements.append(Spacer(1, 6))

        if "notes" in mech:
            for note in mech["notes"]:
                self.elements.append(Paragraph(note, S.STYLE_NOTE))
        self._end_group(g)

    def build_certifications_section(self):
        """Build Section: Certifications."""
        if "certifications" not in self.data:
            return

        g = self._start_group()
        self._add_section("Certifications")
        certs = self.data["certifications"]

        if "table" in certs:
            headers = certs.get("headers", ["Certification", "Region", "Details"])
            rows = certs["table"]
            elems = self._make_table(headers, rows)
            self.elements.extend(elems)
            self.elements.append(Spacer(1, 6))

        if "notes" in certs:
            for note in certs["notes"]:
                self.elements.append(Paragraph(note, S.STYLE_NOTE))
        self._end_group(g)

    def build_company_section(self):
        """Build Section: Company Information."""
        if "company" not in self.data:
            return

        g = self._start_group()
        self._add_section("Company Information")
        company = self.data["company"]

        headers = ["Field", "Details"]
        rows = [[item["field"], item["value"]] for item in company]
        elems = self._make_table(headers, rows,
                                 col_widths=[S.CONTENT_WIDTH * 0.30, S.CONTENT_WIDTH * 0.70])
        self.elements.extend(elems)
        self.elements.append(Spacer(1, 6))
        self._end_group(g)

    def build_references_section(self):
        """Build Section: Reference Documentation."""
        if "references" not in self.data:
            return

        g = self._start_group()
        self._add_section("Reference Documentation")
        refs = self.data["references"]

        headers = ["Reference", "Link / Document"]
        rows = []
        for ref in refs:
            link_text = ref.get("link", ref.get("document", ""))
            rows.append([ref["name"], link_text])

        elems = self._make_table(headers, rows,
                                 col_widths=[S.CONTENT_WIDTH * 0.25, S.CONTENT_WIDTH * 0.75])
        self.elements.extend(elems)
        self.elements.append(Spacer(1, 6))
        self._end_group(g)

    def build_revision_history_section(self):
        """Build Section: Revision History."""
        if "revision_history" not in self.data:
            return

        g = self._start_group()
        self._add_section("Revision History")
        history = self.data["revision_history"]

        headers = ["Date", "Revision", "Changes"]
        rows = [[h["date"], h["revision"], h["changes"]] for h in history]
        elems = self._make_table(headers, rows,
                                 col_widths=[S.CONTENT_WIDTH * 0.18, S.CONTENT_WIDTH * 0.14, S.CONTENT_WIDTH * 0.68])
        self.elements.extend(elems)
        self._end_group(g)

    def _insert_toc(self):
        """Insert table of contents entries at the placeholder position."""
        toc_elements = []
        for level, title, num in self.toc_entries:
            style = S.STYLE_TOC_H1 if level == 1 else S.STYLE_TOC_H2
            prefix = f"{num}" if level == 1 else f"  {num}"
            toc_elements.append(
                Paragraph(f"{prefix}  {title}", style)
            )
        # Insert at placeholder position
        for i, elem in enumerate(toc_elements):
            self.elements.insert(self._toc_insert_index + i, elem)

    def build_generic_section(self, section_data):
        """Build a generic section from data dict with 'title', optional 'text', 'table', etc."""
        sec_num = self._add_section(section_data["title"])

        if "text" in section_data:
            text = section_data["text"]
            if isinstance(text, list):
                for p in text:
                    self.elements.append(Paragraph(p, S.STYLE_BODY))
            else:
                self.elements.append(Paragraph(text, S.STYLE_BODY))

        if "subsections" in section_data:
            for sub in section_data["subsections"]:
                self._add_subsection(sub["title"], sec_num)
                if "text" in sub:
                    self.elements.append(Paragraph(sub["text"], S.STYLE_BODY))
                if "table" in sub:
                    t = sub["table"]
                    elems = self._make_table(t["headers"], t["rows"],
                                             notes=t.get("notes"))
                    self.elements.extend(elems)
                    self.elements.append(Spacer(1, 6))
                if "bullets" in sub:
                    for bullet in sub["bullets"]:
                        self.elements.append(
                            Paragraph(bullet, S.STYLE_BULLET, bulletText="\u2022")
                        )
                if "notes" in sub:
                    for note in sub["notes"]:
                        self.elements.append(Paragraph(note, S.STYLE_NOTE))

        if "bullets" in section_data:
            for bullet in section_data["bullets"]:
                self.elements.append(
                    Paragraph(bullet, S.STYLE_BULLET, bulletText="\u2022")
                )

    def build(self):
        """Build the complete datasheet PDF."""
        meta = self.data["meta"]
        product_name = meta["product_name"]
        modified_date = meta.get("modified_date", date.today().isoformat())
        version = meta.get("version", "Rev 1")
        filename = meta.get("filename", product_name.replace(" ", "-") + "-Datasheet.pdf")
        output_path = os.path.join(self.output_dir, filename)

        os.makedirs(self.output_dir, exist_ok=True)

        # Build document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            leftMargin=S.MARGIN_LEFT,
            rightMargin=S.MARGIN_RIGHT,
            topMargin=S.MARGIN_TOP,
            bottomMargin=S.MARGIN_BOTTOM,
            title=f"OpenMV {product_name} Datasheet",
            author="OpenMV, LLC",
        )

        # Build all sections
        self.build_cover_page()
        self.build_toc_page()

        # Standard sections
        self.build_features_section()
        self.build_ratings_section()
        self.build_connector_section()
        self.build_functional_overview_section()

        # MTBF (generic)
        if "mtbf" in self.data:
            self.build_generic_section(self.data["mtbf"])

        self.build_mechanical_section()

        # Extra generic sections
        for section in self.data.get("extra_sections", []):
            self.build_generic_section(section)

        self.build_certifications_section()
        self.build_company_section()
        self.build_references_section()
        self.build_revision_history_section()

        # Insert TOC entries
        self._insert_toc()

        # Build with header/footer
        logo_path = self._resolve_image("logos/openmv-logo/logo.png")
        header_footer = HeaderFooter(product_name, modified_date, version, logo_path)
        cover_hf = CoverHeaderFooter(product_name, modified_date, version, logo_path)

        # Use cover page template for page 1, standard for rest
        frame = Frame(
            S.MARGIN_LEFT, S.MARGIN_BOTTOM,
            S.CONTENT_WIDTH, S.PAGE_HEIGHT - S.MARGIN_TOP - S.MARGIN_BOTTOM,
            id="normal",
        )

        cover_template = PageTemplate(
            id="cover",
            frames=[frame],
            onPage=cover_hf,
        )
        standard_template = PageTemplate(
            id="standard",
            frames=[frame],
            onPage=header_footer,
        )

        doc.addPageTemplates([cover_template, standard_template])

        # Insert template switch after cover page content
        # Find the first PageBreak and insert NextPageTemplate before it
        from reportlab.platypus import NextPageTemplate
        for i, elem in enumerate(self.elements):
            if isinstance(elem, PageBreak):
                self.elements.insert(i, NextPageTemplate("standard"))
                break

        doc.build(self.elements)
        return output_path
