"""
Shared styles and constants for OpenMV datasheet generation.
"""

from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch, mm
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY

# Page setup
PAGE_SIZE = letter
PAGE_WIDTH, PAGE_HEIGHT = PAGE_SIZE
MARGIN_LEFT = 0.75 * inch
MARGIN_RIGHT = 0.75 * inch
MARGIN_TOP = 0.85 * inch
MARGIN_BOTTOM = 0.75 * inch
CONTENT_WIDTH = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT

# Colors — OpenMV brand blue
OPENMV_BLUE = HexColor("#3F7FBF")
OPENMV_TEAL = OPENMV_BLUE  # legacy alias
OPENMV_DARK = HexColor("#333333")
HEADER_BG = OPENMV_BLUE
HEADER_TEXT = HexColor("#FFFFFF")
TABLE_HEADER_BG = OPENMV_BLUE
TABLE_HEADER_TEXT = HexColor("#FFFFFF")
TABLE_ALT_ROW = HexColor("#EDF3F9")
TABLE_BORDER = HexColor("#CCCCCC")
TEXT_COLOR = HexColor("#333333")
LIGHT_GRAY = HexColor("#F5F5F5")
MEDIUM_GRAY = HexColor("#999999")
LINK_COLOR = OPENMV_BLUE

# Font sizes
TITLE_SIZE = 28
SUBTITLE_SIZE = 14
H1_SIZE = 16
H2_SIZE = 13
H3_SIZE = 11
BODY_SIZE = 9
SMALL_SIZE = 8
FOOTER_SIZE = 7.5
TABLE_HEADER_SIZE = 9
TABLE_BODY_SIZE = 8.5

# Paragraph styles
STYLE_TITLE = ParagraphStyle(
    "Title",
    fontName="Helvetica-Bold",
    fontSize=TITLE_SIZE,
    textColor=OPENMV_DARK,
    leading=TITLE_SIZE * 1.1,
    spaceAfter=2,
)

STYLE_SUBTITLE = ParagraphStyle(
    "Subtitle",
    fontName="Helvetica",
    fontSize=SUBTITLE_SIZE,
    textColor=MEDIUM_GRAY,
    leading=SUBTITLE_SIZE * 1.1,
    spaceAfter=0,
)

STYLE_H1 = ParagraphStyle(
    "Heading1",
    fontName="Helvetica-Bold",
    fontSize=H1_SIZE,
    textColor=OPENMV_TEAL,
    leading=H1_SIZE * 1.3,
    spaceBefore=16,
    spaceAfter=8,
)

STYLE_H2 = ParagraphStyle(
    "Heading2",
    fontName="Helvetica-Bold",
    fontSize=H2_SIZE,
    textColor=OPENMV_DARK,
    leading=H2_SIZE * 1.3,
    spaceBefore=12,
    spaceAfter=6,
)

STYLE_H3 = ParagraphStyle(
    "Heading3",
    fontName="Helvetica-Bold",
    fontSize=H3_SIZE,
    textColor=OPENMV_DARK,
    leading=H3_SIZE * 1.3,
    spaceBefore=8,
    spaceAfter=4,
)

STYLE_BODY = ParagraphStyle(
    "Body",
    fontName="Helvetica",
    fontSize=BODY_SIZE,
    textColor=TEXT_COLOR,
    leading=BODY_SIZE * 1.5,
    spaceAfter=6,
    alignment=TA_JUSTIFY,
)

STYLE_BODY_LEFT = ParagraphStyle(
    "BodyLeft",
    parent=STYLE_BODY,
    alignment=TA_LEFT,
)

STYLE_BULLET = ParagraphStyle(
    "Bullet",
    fontName="Helvetica",
    fontSize=BODY_SIZE,
    textColor=TEXT_COLOR,
    leading=BODY_SIZE * 1.5,
    leftIndent=18,
    bulletIndent=6,
    spaceAfter=3,
)

STYLE_NOTE = ParagraphStyle(
    "Note",
    fontName="Helvetica-Oblique",
    fontSize=SMALL_SIZE,
    textColor=MEDIUM_GRAY,
    leading=SMALL_SIZE * 1.4,
    spaceAfter=4,
    leftIndent=6,
)

STYLE_TABLE_HEADER = ParagraphStyle(
    "TableHeader",
    fontName="Helvetica-Bold",
    fontSize=TABLE_HEADER_SIZE,
    textColor=TABLE_HEADER_TEXT,
    leading=TABLE_HEADER_SIZE * 1.3,
    alignment=TA_LEFT,
)

STYLE_TABLE_BODY = ParagraphStyle(
    "TableBody",
    fontName="Helvetica",
    fontSize=TABLE_BODY_SIZE,
    textColor=TEXT_COLOR,
    leading=TABLE_BODY_SIZE * 1.4,
    alignment=TA_LEFT,
)

STYLE_TABLE_BODY_BOLD = ParagraphStyle(
    "TableBodyBold",
    fontName="Helvetica-Bold",
    fontSize=TABLE_BODY_SIZE,
    textColor=TEXT_COLOR,
    leading=TABLE_BODY_SIZE * 1.4,
    alignment=TA_LEFT,
)

STYLE_TABLE_BODY_CENTER = ParagraphStyle(
    "TableBodyCenter",
    parent=STYLE_TABLE_BODY,
    alignment=TA_CENTER,
)

STYLE_LINK = ParagraphStyle(
    "Link",
    fontName="Helvetica",
    fontSize=BODY_SIZE,
    textColor=LINK_COLOR,
    leading=BODY_SIZE * 1.5,
)

STYLE_FOOTER = ParagraphStyle(
    "Footer",
    fontName="Helvetica",
    fontSize=FOOTER_SIZE,
    textColor=MEDIUM_GRAY,
    leading=FOOTER_SIZE * 1.3,
)

STYLE_SKU = ParagraphStyle(
    "SKU",
    fontName="Helvetica",
    fontSize=9,
    textColor=MEDIUM_GRAY,
    leading=11,
    spaceAfter=4,
)

# Cover page: product name right-aligned in the banner row
STYLE_COVER_PRODUCT_NAME = ParagraphStyle(
    "CoverProductName",
    fontName="Helvetica-Bold",
    fontSize=14,
    textColor=OPENMV_DARK,
    leading=17,
    alignment=TA_RIGHT,
)

# Cover page: "Datasheet" label, right-aligned
STYLE_COVER_DATASHEET_LABEL = ParagraphStyle(
    "CoverDatasheetLabel",
    fontName="Helvetica",
    fontSize=12,
    textColor=OPENMV_DARK,
    leading=15,
    alignment=TA_RIGHT,
    spaceAfter=2,
)

# Cover page: SKU right-aligned
STYLE_COVER_SKU_RIGHT = ParagraphStyle(
    "CoverSKURight",
    fontName="Courier",
    fontSize=10,
    textColor=OPENMV_DARK,
    leading=13,
    alignment=TA_RIGHT,
    spaceAfter=4,
)

STYLE_COVER_DESCRIPTION = ParagraphStyle(
    "CoverDescription",
    fontName="Helvetica",
    fontSize=10,
    textColor=TEXT_COLOR,
    leading=14,
    spaceAfter=10,
    alignment=TA_JUSTIFY,
)

STYLE_FEATURE_BULLET = ParagraphStyle(
    "FeatureBullet",
    fontName="Helvetica",
    fontSize=9,
    textColor=TEXT_COLOR,
    leading=13,
    leftIndent=18,
    bulletIndent=6,
    spaceAfter=4,
)

STYLE_TOC_H1 = ParagraphStyle(
    "TOCH1",
    fontName="Helvetica-Bold",
    fontSize=11,
    textColor=OPENMV_DARK,
    leading=18,
    leftIndent=0,
)

STYLE_TOC_H2 = ParagraphStyle(
    "TOCH2",
    fontName="Helvetica",
    fontSize=10,
    textColor=TEXT_COLOR,
    leading=16,
    leftIndent=20,
)
