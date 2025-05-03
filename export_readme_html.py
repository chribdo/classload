import os
import re
import sys
import base64
import markdown
from pathlib import Path

def get_resource_path(filename):
    """
    Gibt den Pfad zur Datei zurück – funktioniert mit PyInstaller, py2app und lokal.
    """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    elif hasattr(sys, 'frozen') and 'RESOURCEPATH' in os.environ:
        return os.path.join(os.environ['RESOURCEPATH'], filename)
    else:
        # Lokaler Entwicklungsmodus – Bezug relativ zur Datei
        base_path = Path(__file__).resolve().parent
        return str(base_path / filename)

def image_to_data_url(path: str) -> str:
    """
    Wandelt ein Bild in eine base64-HTML-URL um.
    """
    mime = "image/png"
    data = Path(path).read_bytes()
    b64 = base64.b64encode(data).decode()
    return f"data:{mime};base64,{b64}"

def export_html(md_path: str, screenshot_path: str, out_path: str):
    """
    Wandelt README.md in formatierte HTML-Datei mit eingebettetem Screenshot.
    """
    md_text = Path(md_path).read_text(encoding="utf-8")

    # Screenshot ersetzen, falls vorhanden
    if Path(screenshot_path).exists():
        data_url = image_to_data_url(screenshot_path)
        html_img = f'<img src="{data_url}" alt="Screenshot" style="max-width:100%; margin-top:1em;">'
        md_text = re.sub(r'!\[.*?\]\([^)]+\)', html_img, md_text)

    # Markdown → HTML
    html_body = markdown.markdown(md_text, extensions=["extra", "sane_lists", "tables", "nl2br"])

    # HTML-Template mit Stil
    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="utf-8">
    <title>Hilfe</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            padding: 2em;
            max-width: 800px;
            margin: auto;
            background-color: #f8f9fa;
            color: #212529;
        }}
        img {{
            border: 1px solid #ccc;
            border-radius: 6px;
            max-width: 100%;
        }}
        h1, h2, h3 {{
            color: #0d6efd;
        }}
        pre {{
            background: #333;
            color: #f8f8f2;
            padding: 1em;
            border-radius: 6px;
            overflow-x: auto;
        }}
        code {{
            background: #eee;
            padding: 2px 4px;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
{html_body}
</body>
</html>
"""
    # HTML speichern
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(html, encoding="utf-8")
    print(f"[OK] HTML exportiert nach: {out_path}")

# Einstiegspunkt
if __name__ == "__main__":
    readme = get_resource_path("README.md")
    screenshot = get_resource_path("screenshot.png")
    export_html(readme, screenshot, "hilfe.html")

