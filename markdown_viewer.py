import os
import markdown
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl
import sys
from PySide6.QtWidgets import QApplication

app = None  # wird später initialisiert

class MarkdownViewer(QMainWindow):
    def __init__(self, md_file):
        super().__init__()
        self.setWindowTitle("Markdown Viewer")
        self.resize(900, 700)

        # Markdown lesen und in HTML umwandeln
        html_content = self.convert_markdown_to_html(md_file)

        # Basispfad für lokale Ressourcen (z. B. Bilder wie screenshot.png)
        base_path = QUrl.fromLocalFile(os.path.abspath(os.path.dirname(md_file)) + os.sep)

        # WebView erzeugen und HTML laden
        self.browser = QWebEngineView()
        self.browser.setHtml(html_content, base_path)
        self.setCentralWidget(self.browser)

    def convert_markdown_to_html(self, filepath):
        if not os.path.exists(filepath):
            return "<h1>Datei nicht gefunden</h1>"

        with open(filepath, "r", encoding="utf-8") as file:
            md_text = file.read()

        html = markdown.markdown(md_text, extensions=["extra", "tables", "sane_lists"])

        # Optionales Basis-HTML-Template mit CSS
        return f"""
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 40px;
                    line-height: 1.6;
                    background-color: #f8f9fa;
                    color: #212529;
                }}
                h1, h2, h3 {{
                    color: #0030ff;
                }}
                code {{
                    background-color: #eee;
                    padding: 2px 4px;
                    border-radius: 4px;
                    font-family: monospace;
                }}
                pre {{
                    background: #333;
                    color: #f8f8f2;
                    padding: 10px;
                    border-radius: 5px;
                    overflow-x: auto;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                }}
                table, th, td {{
                    border: 1px solid #ccc;
                    padding: 8px;
                }}
                ul, ol {{
                    margin-left: 20px;
                }}
                img {{
                    max-width: 100%;
                    height: auto;
                    border: 1px solid #ccc;
                    margin: 10px 0;
                }}
            </style>
        </head>
        <body>{html}</body>
        </html>
        """

def start_markdown_viewer(readme_path: str):
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
        viewer = MarkdownViewer(readme_path)
        viewer.show()
        sys.exit(app.exec())
    else:
        viewer = MarkdownViewer(readme_path)
        viewer.show()


"""
if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = MarkdownViewer("README.md")  # Pfad ggf. anpassen
    viewer.show()
    sys.exit(app.exec())
    
"""
