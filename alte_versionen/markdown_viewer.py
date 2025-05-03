import os
import re
import markdown
import webview
import base64
from pathlib import Path

def image_to_data_url(path: str):
    """Wandelt ein Bild in eine data:-URL um (für pywebview)."""
    image_path = Path(path)
    if not image_path.exists():
        return None
    mime = "image/png"
    b64 = base64.b64encode(image_path.read_bytes()).decode()
    return f"data:{mime};base64,{b64}"

def start_markdown_viewer(readme_path: str, screenshot_path: str = None):
    if not os.path.exists(readme_path):
        html = "<h1>README nicht gefunden</h1>"
    else:
        with open(readme_path, "r", encoding="utf-8") as f:
            md_text = f.read()

        # 🔄 Screenshot in Base64-Daten-URL einbetten
        if screenshot_path and os.path.exists(screenshot_path):
            data_url = image_to_data_url(screenshot_path)
            if data_url:
                image_tag = f'<img src="{data_url}" alt="Screenshot" style="max-width:100%;border:1px solid #ccc;border-radius:6px;margin-top:1em;">'
                # Ersetze Markdown-Bild (z. B. ![Screenshot](screenshot.png))
                md_text = re.sub(r'!\[.*?\]\([^)]+\)', image_tag, md_text)

        # Markdown → HTML
        html = markdown.markdown(md_text, extensions=["extra", "sane_lists", "tables", "nl2br"])

    # HTML-Rahmen mit CSS-Stil
    html_template = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                padding: 2em;
                background-color: #f8f9fa;
                color: #212529;
                max-width: 800px;
                margin: auto;
            }}
            h1, h2, h3 {{
                color: #0d6efd;
            }}
            pre {{
                background: #333;
                color: #eee;
                padding: 1em;
                border-radius: 4px;
                overflow-x: auto;
            }}
            code {{
                background: #eee;
                padding: 0.2em 0.4em;
                border-radius: 4px;
            }}
            img {{
                display: block;
                margin: 1em auto;
            }}
        </style>
    </head>
    <body>
        {html}
    </body>
    </html>
    """

    webview.create_window("Hilfe", html=html_template)
    webview.start()
