#!/usr/bin/env python3
"""Convert hormuz_research_report.md to styled HTML report."""

import markdown
from pathlib import Path
import re

def read_css_template():
    """Extract CSS from existing HTML file."""
    html_path = Path(__file__).parent / "hormuz_research_report.html"
    if not html_path.exists():
        return ""
    content = html_path.read_text()
    match = re.search(r'<style>(.*?)</style>', content, re.DOTALL)
    return match.group(1) if match else ""

def convert_md_to_html(md_text: str) -> str:
    """Convert markdown to HTML body content."""
    # Use markdown library with extensions
    extensions = ['tables', 'fenced_code', 'nl2br']
    html_body = markdown.markdown(md_text, extensions=extensions)
    return html_body

def post_process_html(html: str) -> str:
    """Add CSS classes and enhance HTML output."""
    # Make tables responsive
    html = html.replace('<table>', '<table class="report-table">')

    # Add footnote styling to bracketed superscript references like [10]
    html = re.sub(
        r'\[(\d+)\]',
        r'<sup class="fn"><a href="#fn\1">[\1]</a></sup>',
        html
    )

    return html

def build_html(css: str, body: str, subtitle: str) -> str:
    """Assemble full HTML document."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Strait of Hormuz Crisis: Oil Supply Disruption Briefing</title>
<style>
{css}
</style>
</head>
<body>

<h1>Strait of Hormuz Crisis</h1>
<p class="subtitle">Oil &amp; Gas Supply Disruption Briefing &mdash; <span>April 10, 2026 (Day 42)</span> &mdash; Last refreshed: Apr 10, 2026 (comprehensive research sweep) &mdash; <strong>Islamabad PROXIMITY TALKS ongoing:</strong> Ghalibaf sets 2 preconditions (Lebanon ceasefire + frozen assets); separate rooms; GL 134A expires TONIGHT; net shortage widened to ~13 mb/d; Mojtaba Khamenei reportedly incapacitated; 11th MEU arriving imminently; ~5&ndash;7 ships/day vs. 135 normal; Brent $96.66 (+0.77%); gasoline $4.17/gal; diesel $5.43/gal; TTF &euro;44.46/MWh</p>

{body}

</body>
</html>"""

def main():
    base = Path(__file__).parent
    md_path = base / "hormuz_research_report.md"
    html_out = base / "hormuz_research_report.html"

    # Read markdown
    md_text = md_path.read_text()

    # Extract subtitle from first few lines (the bold status line)
    subtitle = ""

    # Get CSS from existing HTML
    css = read_css_template()

    # Convert markdown to HTML
    body_html = convert_md_to_html(md_text)

    # Post-process
    body_html = post_process_html(body_html)

    # Build full document
    full_html = build_html(css, body_html, subtitle)

    # Write output
    html_out.write_text(full_html)
    print(f"Generated {html_out} ({len(full_html):,} bytes)")

if __name__ == "__main__":
    main()
