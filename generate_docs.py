import subprocess
import sys
import os
sys.path.insert(0, os.path.abspath("."))

OUTPUT_DIR = "docs"

# Nur explizit freigegebene Module
MODULES = [
    "tk_main_menue",
    "tk_klassen_uploader_app",
    "tk_jamf_login",
    "jamfscripts"
]

def main():
    if os.path.exists(OUTPUT_DIR):
        print(f"🧹 Lösche vorhandenes Verzeichnis: {OUTPUT_DIR}")
        subprocess.run(["rm", "-rf", OUTPUT_DIR])

    print("📄 Generiere Dokumentation mit pdoc für:")
    for m in MODULES:
        print(f"  - {m}")

    subprocess.run(["pdoc", *MODULES, "-o", OUTPUT_DIR], check=True)
    print(f"✅ Dokumentation gespeichert in: {OUTPUT_DIR}/index.html")

if __name__ == "__main__":
    main()

