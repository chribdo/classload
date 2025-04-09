from tk_jamf_login import JamfLogin
from tkinter import filedialog, messagebox, scrolledtext, simpledialog
from datetime import timedelta

from ttkbootstrap.dialogs import *
from tkhtmlview import HTMLLabel
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.scrolled import ScrolledText
from jamfscripts import *
import os, sys, markdown, getpass
import platform
from pathlib import Path

JAMF_URL = ""
TOKEN = ""
ZUSTIMMUNGSDATEI = os.path.join(os.getcwd(), "zustimmung.json")
NUTZUNGSDATEI = os.path.join(os.getcwd(), "nutzung.json")


def init_dpi_awareness():
    """
    Aktiviert DPI-Awareness unter Windows, um eine scharfe und korrekt skalierte
    Darstellung in tkinter/ttkbootstrap-Fenstern zu gewährleisten.
    Hat keinen Effekt auf macOS oder Linux.
    """
    if sys.platform.startswith("win"):
        try:
            import ctypes
            # 1 = system DPI aware, 2 = per-monitor DPI aware
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass


def get_resource_path(filename):
    """
    Gibt den Pfad zur Datei zurück – funktioniert mit PyInstaller, py2app und lokal.
    """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    elif hasattr(sys, 'frozen') and 'RESOURCEPATH' in os.environ:
        return os.path.join(os.environ['RESOURCEPATH'], filename)
    else:
        # Lokaler Entwicklungsmodus – Bezug relativ zur Python-Datei
        base_path = Path(__file__).resolve().parent
        return str(base_path / filename)


LIZENZ = get_resource_path("LICENSE.txt")


def lade_nutzungsinfo():
    """

    Returns:

    """
    if os.path.exists(NUTZUNGSDATEI):
        with open(NUTZUNGSDATEI, "r") as f:
            return json.load(f)
    return {}


def speichere_nutzungsinfo(info):
    with open(NUTZUNGSDATEI, "w") as f:
        json.dump(info, f)


def pruefe_nutzungsart():
    info = lade_nutzungsinfo()
    if "nutzung" not in info:
        nutzungsart = zeige_nutzungsdialog()
        if not nutzungsart:
            Messagebox.ok(title="Abbruch", message="Nutzungstyp nicht festgelegt. Programm wird beendet.", alert=True)
            sys.exit()
        if not nutzungsart:
            Messagebox.ok(title="Abbruch", message="Nutzungstyp nicht festgelegt. Programm wird beendet.", alert=True)
            sys.exit()
        nutzungsart = nutzungsart.strip().lower()
        info["nutzung"] = nutzungsart
        if nutzungsart == "gewerblich":
            info["startdatum"] = datetime.today().strftime("%Y-%m-%d")
        speichere_nutzungsinfo(info)
    elif info["nutzung"] == "gewerblich":
        startdatum = datetime.strptime(info["startdatum"], "%Y-%m-%d")
        verbleibend = (startdatum + timedelta(days=7)) - datetime.today()
        if verbleibend.days < 0:
            Messagebox.ok(title="Testzeitraum abgelaufen",
                          message="Die 7-Tage-Testversion ist abgelaufen. Bitte kontaktieren Sie den Entwickler für eine Lizenz.",
                          alert=True)
            sys.exit()
        else:
            Messagebox.ok(title="Testversion",
                          message=f"Testversion aktiv. Noch {verbleibend.days + 1} Tage verfügbar.", alert=False)


def zeige_lizenz():
    if not os.path.exists(LIZENZ):
        Messagebox.ok(title="Lizenz", message="LICENSE.txt nicht gefunden.", alert=False)
        return
    lizfenster = tk.Toplevel()
    lizfenster.title("Lizenz")
    lizfenster.geometry("600x500")
    textfeld = scrolledtext.ScrolledText(lizfenster, wrap="word")
    with open(LIZENZ, "r", encoding="utf-8") as f:
        textfeld.insert("1.0", f.read())
    textfeld.config(state="disabled")
    lizfenster.update_idletasks()
    lizfenster.minsize(lizfenster.winfo_width(), lizfenster.winfo_height())
    textfeld.pack(fill="both", expand=True)


def zeige_nutzungsdialog():
    auswahlfenster = tk.Toplevel()
    auswahlfenster.title("Nutzungsart wählen")
    auswahlfenster.geometry("500x300")
    auswahlfenster.grab_set()
    auswahlfenster.resizable(False, True)
    auswahlfenster.update_idletasks()
    auswahlfenster.minsize(auswahlfenster.winfo_width(), auswahlfenster.winfo_height())

    auswahl = tk.StringVar()
    auswahl.set("privat")

    def bestätigen():
        auswahlfenster.destroy()

    label = ttk.Label(auswahlfenster, text="Bitte wählen Sie die Art der Nutzung:")
    label.pack(pady=10)

    r1 = ttk.Radiobutton(auswahlfenster, text="Privat/Schule (dauerhaft erlaubt)", variable=auswahl, value="privat")
    r2 = ttk.Radiobutton(auswahlfenster, text="Gewerblich/Testversion (7 Tage)", variable=auswahl, value="gewerblich")
    r1.pack(anchor="w", padx=30, pady=5)
    r2.pack(anchor="w", padx=30, pady=5)

    button = ttk.Button(auswahlfenster, text="Bestätigen", command=bestätigen)
    button.pack(pady=20)

    auswahlfenster.wait_window()
    return auswahl.get()


def zeige_about_dialog():
    about = tk.Toplevel()
    about.title("Über dieses Tool")
    about.geometry("400x200")
    about.resizable(False, False)

    frame = ttk.Frame(about, padding=20)
    frame.pack(fill="both", expand=True)

    label = ttk.Label(frame, text="macOS Tool für JAMF-Interaktionen\nVersion 1.0.0\n© 2025 von Dir", justify="center",
                      font=("Helvetica", 12))
    label.pack(pady=(10, 20))

    btn = ttk.Button(frame, text="Schließen", command=about.destroy)
    btn.pack(pady=(10, 0))


# --- Lizenzdialog + Zustimmungsspeicherung ---


def zustimmung_bereits_erfolgt():
    if os.path.exists(ZUSTIMMUNGSDATEI):
        try:
            with open(ZUSTIMMUNGSDATEI, "r") as f:
                data = json.load(f)
                return data.get("zugestimmt", False)
        except Exception:
            return False
    return False


def speichere_zustimmung():
    with open(ZUSTIMMUNGSDATEI, "w") as f:
        json.dump({"zugestimmt": True}, f)


def show_license_dialog(root):
    license_text = ""
    try:
        with open(LIZENZ, "r", encoding="utf-8") as f:
            license_text = f.read()
    except FileNotFoundError:
        Messagebox.show_error("LICENSE.txt nicht gefunden.", "Fehler", parent=root)
        return False

    dialog = ttk.Toplevel(root)
    dialog.title("Lizenzvereinbarung")
    dialog.geometry("700x500")
    dialog.transient(root)
    dialog.grab_set()

    label = ttk.Label(dialog, text="Bitte lesen Sie die Lizenzbedingungen:", font=("Helvetica", 12))
    label.pack(pady=10)

    text_area = ScrolledText(dialog, height=22, autohide=True)
    text_area.insert("1.0", license_text)
    text_area.text.configure(state="disabled")
    text_area.pack(padx=20, pady=20, fill="both", expand=True)

    result = {"accepted": None}

    def agree():
        result["accepted"] = True
        dialog.destroy()

    def disagree():
        result["accepted"] = False
        dialog.destroy()

    button_frame = ttk.Frame(dialog)
    button_frame.pack(pady=10)

    ttk.Button(button_frame, text="Ich stimme zu", command=agree, bootstyle="success").pack(side="left", padx=10)
    ttk.Button(button_frame, text="Ich lehne ab", command=disagree, bootstyle="danger").pack(side="right", padx=10)

    dialog.wait_window()  # blockiert, bis dialog geschlossen

    return result["accepted"]


def show_help(root):
    help_text = load_markdown_file("HILFE.md")
    show_markdown_window(root, "Hilfe", help_text)


def load_markdown_file(filename):
    if not os.path.exists(filename):
        return f"Datei '{filename}' nicht gefunden."
    with open(filename, "r", encoding="utf-8") as f:
        return markdown.markdown(f.read())


def show_markdown_window(root, title, html_content):
    window = ttk.Toplevel(root)
    window.title(title)
    window.geometry("600x400")
    html_label = HTMLLabel(window, html=html_content)
    html_label.pack(fill="both", expand=True, padx=10, pady=10)


def show_about():
    messagebox.showinfo("Über Classload", "Classload\nVersion 1.0\n(c) 2025")


def main():
    init_dpi_awareness()
    root = ttk.Window(themename="cosmo")
    if sys.platform.startswith("win"):
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.ico")
            root.iconbitmap(icon_path)
        except Exception as e:
            print(f"Icon konnte nicht gesetzt werden: {e}")
    if not zustimmung_bereits_erfolgt():
        if not show_license_dialog(root):
            return
        speichere_zustimmung()

    menubar = tk.Menu(root)
    hilfe_menu = tk.Menu(menubar, tearoff=0)
    hilfe_menu.add_command(label="Lizenz anzeigen", command=zeige_lizenz)
    hilfe_menu.add_command(label="Hilfe anzeigen", command=lambda: show_help(root))

    if platform.system() == "Darwin":
        apple_menu = tk.Menu(menubar, name="apple", tearoff=0)
        apple_menu.add_command(label="Über Classload", command=show_about)
        menubar.add_cascade(menu=apple_menu)
        menubar.add_cascade(label="Hilfe", menu=hilfe_menu)
        root["menu"] = menubar
    else:
        menubar.add_command(label="Über Classload", command=show_about)
        menubar.add_cascade(label="Hilfe", menu=hilfe_menu)
        root.config(menu=menubar)
    # menubar.add_cascade(label="Hilfe", menu=hilfe_menu)
    root.config(menu=menubar)

    root.withdraw()  # root bleibt im Hintergrund, aber notwendig für Tkinter
    # Nutzungsprüfung beim Start
    pruefe_nutzungsart()
    login = JamfLogin(root)
    root.mainloop()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback

        with open("/tmp/classload_error.log", "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        raise
