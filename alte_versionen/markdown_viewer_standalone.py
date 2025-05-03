import sys
import os
from markdown_viewer import start_markdown_viewer
from tk_main_menue import get_resource_path

# 💡 Ermittle Pfade mit Fallback
readme = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.abspath("README.md")
screenshot = (
    os.path.abspath(sys.argv[2])
    if len(sys.argv) > 2
    else get_resource_path("screenshot.png")
)

# 📋 Debug-Ausgabe (optional)
print("📄 README:", readme)
print("📷 Screenshot:", screenshot)

# 🖥️ Viewer starten
start_markdown_viewer(readme, screenshot)
