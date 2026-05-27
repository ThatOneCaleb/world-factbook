#!/usr/bin/env python3
"""
Generate a formatted PDF from country data JSON.

Usage: python3 tools/generate_pdf.py .tmp/norway_data.json
Output: PDF file saved to .tmp/{country}_report.pdf
"""

import json
import os
import re
import sys
import textwrap
from fpdf import FPDF


def sanitize(text):
    """Replace unicode characters that Helvetica can't render."""
    replacements = {
        '\u2014': '--', '\u2013': '-', '\u2018': "'", '\u2019': "'",
        '\u201c': '"', '\u201d': '"', '\u2026': '...', '\u00a0': ' ',
        '\u2010': '-', '\u2011': '-', '\u2012': '-',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    # Strip any remaining non-latin-1 characters
    return text.encode('latin-1', errors='replace').decode('latin-1')


class CountryPDF(FPDF):
    def __init__(self, country_name):
        super().__init__()
        self.country_name = country_name

    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 10, f"{self.country_name} - Standard of Living Data", ln=True, align="C")
        self.set_font("Helvetica", "", 9)
        self.cell(0, 5, "Source: CIA World Factbook (factbook.json) + UNDP HDR", ln=True, align="C")
        self.ln(3)
        self.set_draw_color(0, 0, 0)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def add_category(self, title):
        self.set_font("Helvetica", "B", 13)
        self.set_fill_color(41, 65, 122)
        self.set_text_color(255, 255, 255)
        self.cell(0, 8, f"  {title}", ln=True, fill=True)
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def add_field(self, label, value, row_index=0):
        if row_index % 2 == 0:
            self.set_fill_color(240, 240, 245)
        else:
            self.set_fill_color(255, 255, 255)

        value = sanitize(str(value)) if value else "N/A"

        # Wrap long values
        max_val_width = 120
        self.set_font("Helvetica", "", 8)
        wrapped_lines = []
        for line in value.split("; "):
            wrapped = textwrap.wrap(line, width=85)
            wrapped_lines.extend(wrapped if wrapped else [""])

        line_height = 5
        block_height = max(line_height * len(wrapped_lines), line_height)

        # Check if we need a new page
        if self.get_y() + block_height > 275:
            self.add_page()

        x_start = self.get_x()
        y_start = self.get_y()

        # Draw background
        self.rect(10, y_start, 190, block_height, "F")

        # Label
        self.set_font("Helvetica", "B", 9)
        self.set_xy(12, y_start)
        self.cell(60, line_height, label, ln=False)

        # Value
        self.set_font("Helvetica", "", 8)
        self.set_xy(72, y_start)
        for i, wl in enumerate(wrapped_lines):
            self.set_xy(72, y_start + i * line_height)
            self.cell(max_val_width, line_height, wl, ln=False)

        self.set_y(y_start + block_height)


CATEGORY_LABELS = {
    "category_geography": "Geography",
    "category_people": "People",
    "category_government": "Government",
    "category_economy": "Economy",
    "category_military": "Military",
    "category_different_source": "Different Source (UNDP)",
}


def generate_pdf(json_path):
    with open(json_path) as f:
        data = json.load(f)

    country = data["country"]
    pdf = CountryPDF(country)
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)

    row_idx = 0
    for cat_key, cat_label in CATEGORY_LABELS.items():
        cat_data = data.get(cat_key, {})
        if not cat_data:
            continue
        pdf.add_category(cat_label)
        for field_name, field_value in cat_data.items():
            pdf.add_field(field_name, field_value, row_idx)
            row_idx += 1
        pdf.ln(3)

    # Save PDF
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tmp_dir = os.path.join(base_dir, ".tmp")
    os.makedirs(tmp_dir, exist_ok=True)
    safe_name = re.sub(r'[^a-z0-9]', '_', country.lower().strip())
    out_path = os.path.join(tmp_dir, f"{safe_name}_report.pdf")

    pdf.output(out_path)
    print(f"SUCCESS: PDF saved to {out_path}")
    return out_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 tools/generate_pdf.py .tmp/country_data.json")
        sys.exit(1)
    generate_pdf(sys.argv[1])
