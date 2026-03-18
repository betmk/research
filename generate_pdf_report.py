"""
Generate a mobile-friendly PDF version of the Hormuz crisis briefing.
Converts the Markdown report to styled HTML, then renders to PDF via WeasyPrint.
"""

import markdown
from weasyprint import HTML
from pathlib import Path

REPORT_MD = Path(__file__).parent / "hormuz_research_report.md"
OUTPUT_PDF = Path(__file__).parent / "hormuz_research_report.pdf"

# Read markdown source
md_text = REPORT_MD.read_text(encoding="utf-8")

# Convert to HTML
html_body = markdown.markdown(
    md_text,
    extensions=["tables", "smarty", "toc"],
)

# Wrap in a full HTML document with mobile-friendly styling
full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<style>
@page {{
    size: A4;
    margin: 1.5cm 1.2cm;
    @bottom-center {{
        content: counter(page) " / " counter(pages);
        font-size: 8pt;
        color: #888;
    }}
}}
body {{
    font-family: -apple-system, "Helvetica Neue", Arial, sans-serif;
    font-size: 10pt;
    line-height: 1.5;
    color: #1a1a1a;
    max-width: 100%;
}}
h1 {{
    font-size: 18pt;
    color: #b91c1c;
    border-bottom: 2px solid #b91c1c;
    padding-bottom: 6pt;
    margin-top: 0;
}}
h2 {{
    font-size: 14pt;
    color: #1e3a5f;
    border-bottom: 1px solid #ccc;
    padding-bottom: 4pt;
    margin-top: 18pt;
    page-break-after: avoid;
}}
h3 {{
    font-size: 11pt;
    color: #374151;
    margin-top: 12pt;
    page-break-after: avoid;
}}
p {{
    margin: 6pt 0;
    text-align: justify;
}}
table {{
    width: 100%;
    border-collapse: collapse;
    margin: 10pt 0;
    font-size: 8.5pt;
    page-break-inside: avoid;
}}
th {{
    background-color: #1e3a5f;
    color: white;
    padding: 5pt 6pt;
    text-align: left;
    font-weight: 600;
}}
td {{
    padding: 4pt 6pt;
    border-bottom: 1px solid #ddd;
    vertical-align: top;
}}
tr:nth-child(even) td {{
    background-color: #f8f9fa;
}}
strong {{
    color: #1a1a1a;
}}
ul, ol {{
    margin: 6pt 0;
    padding-left: 18pt;
}}
li {{
    margin: 3pt 0;
}}
hr {{
    border: none;
    border-top: 1px solid #ddd;
    margin: 14pt 0;
}}
a {{
    color: #2563eb;
    text-decoration: none;
}}
code {{
    background: #f3f4f6;
    padding: 1pt 3pt;
    border-radius: 2pt;
    font-size: 9pt;
}}
/* Sources section: smaller text */
h2:last-of-type ~ ul {{
    font-size: 7.5pt;
    line-height: 1.4;
}}
</style>
</head>
<body>
{html_body}
</body>
</html>
"""

try:
    HTML(string=full_html).write_pdf(str(OUTPUT_PDF))
    print(f"PDF saved to: {OUTPUT_PDF}")
    print(f"File size: {OUTPUT_PDF.stat().st_size / 1024:.0f} KB")
except Exception as e:
    print(f"Error generating PDF: {e}")
    raise
