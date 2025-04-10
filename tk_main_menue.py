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
global iconpic

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

import sys
import os
import tkinter as tk

def set_window_icon(widget):
    try:
        if sys.platform == "darwin":
            # macOS: kleineres Icon verwenden, sonst kommt "path is bad"
            icon_relpath = os.path.join("assets", "icon_small.png")
        else:
            # Windows/Linux: großes Icon mit Alpha verwenden
            icon_relpath = os.path.join("assets", "icon.png")

        icon_path = get_resource_path(icon_relpath)
        print(f"🖼 Verwende Icon: {icon_path}")

        icon_img = tk.PhotoImage(file=icon_path)
        widget.iconphoto(True, icon_img)
        widget.icon_img = icon_img  # Referenz halten!
    except Exception as e:
        print(f"⚠️ Icon konnte nicht gesetzt werden: {e}")



LIZENZ = get_resource_path("LICENSE.txt")
"""
def set_window_icon(widget):
    try:
        icon_path = os.path.join("assets", "icon.png")
        icon_img = tk.PhotoImage(file=icon_path)
        widget.iconphoto(True, icon_img)
        widget.icon_img = icon_img
    except:
        pass

def set_window_icon(widget):
    try:
        icon_path = get_resource_path(os.path.join("assets", "icon.png"))
        icon_img = tk.PhotoImage(file=icon_path)
        widget.iconphoto(True, icon_img)
        widget.icon_img = icon_img  # Referenz halten!
    except Exception as e:
        print(f"Icon konnte nicht gesetzt werden: {e}")
"""
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

def pruefe_testversion(root, verbleibend):
    root.deiconify()
    #root.geometry("400x300")  # Fenstergröße setzen
    root.minsize(400, 250)
    if verbleibend.days < 0:
        def beenden():
            root.destroy()
            sys.exit()

        frame = ttk.Frame(root, padding=30)
        frame.pack(expand=True)
        label = ttk.Label(frame,
                          text="❌ Die 7-Tage-Testversion ist abgelaufen.\nBitte kontaktieren Sie den Entwickler für eine Lizenz.",
                          font=("Arial", 12), justify="center")
        label.pack()
        root.after(5000, beenden)  # Automatisch schließen & Programm beenden
    else:
        def weiter():
            JamfLogin(root)
            hinweis.destroy()
            root.withdraw()

        hinweis = ttk.Frame(root, padding=20)
        hinweis.place(relx=0.5, rely=0.5, anchor="center")

        label = ttk.Label(hinweis, text=f"✔ Testversion aktiv\nNoch {verbleibend.days + 1} Tage verfügbar", font=("Arial", 11))
        label.pack(pady=(0, 10))

        btn = ttk.Button(hinweis, text="OK", command=weiter)
        btn.pack()
        root.update_idletasks()
        root.minsize(root.winfo_width(), root.winfo_height())


def pruefe_nutzungsart(root):
    info = lade_nutzungsinfo()
    if "nutzung" not in info:
        nutzungsart = zeige_nutzungsdialog(root)
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
    elif info["nutzung"] == "privat":
        JamfLogin(root)
    elif info["nutzung"] == "gewerblich":
        startdatum = datetime.strptime(info["startdatum"], "%Y-%m-%d")
        verbleibend = (startdatum + timedelta(days=7)) - datetime.today()
        """
        if verbleibend.days < 0:
            Messagebox.ok(title="Testzeitraum abgelaufen",
                          message="Die 7-Tage-Testversion ist abgelaufen. Bitte kontaktieren Sie den Entwickler für eine Lizenz.",
                          alert=True)
            sys.exit()
        else:
            Messagebox.ok(title="Testversion",
                          message=f"Testversion aktiv. Noch {verbleibend.days + 1} Tage verfügbar.", alert=False)
        """
        pruefe_testversion(root, verbleibend)


def zeige_lizenz():
    if not os.path.exists(LIZENZ):
        Messagebox.ok(title="Lizenz", message="LICENSE.txt nicht gefunden.", alert=False)
        return
    lizfenster = tk.Toplevel()
    #set_window_icon(lizfenster)
    lizfenster.title("Lizenz")
    lizfenster.geometry("600x500")
    textfeld = scrolledtext.ScrolledText(lizfenster, wrap="word")
    with open(LIZENZ, "r", encoding="utf-8") as f:
        textfeld.insert("1.0", f.read())
    textfeld.config(state="disabled")
    lizfenster.update_idletasks()
    lizfenster.minsize(lizfenster.winfo_width(), lizfenster.winfo_height())
    textfeld.pack(fill="both", expand=True)


def zeige_nutzungsdialog(root):
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
        JamfLogin(root)
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
    #set_window_icon(about)
    about.title("Über Classload")
    about.geometry("400x200")
    about.resizable(True, True)

    frame = ttk.Frame(about, padding=20)
    frame.pack(fill="both", expand=True)

    label = ttk.Label(frame, text="Classload\nsendet Daten zu Geräten, Nutzenden und Kursen an Jamf\nVersion 0.9\n© 2025 Christiane Borchel", justify="center",
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
    try:
        with open(LIZENZ, "r", encoding="utf-8") as f:
            license_text = f.read()
    except FileNotFoundError:
        Messagebox.show_error("LICENSE.txt nicht gefunden.", "Fehler", parent=root)
        return False

    if sys.platform == "darwin":
      dialog = ttk.Toplevel(root)
    else:
       dialog = ttk.Toplevel(root, iconphoto=None)
    #set_window_icon(dialog)
    dialog.title("Lizenzvereinbarung")
    dialog.minsize(700, 500)
    dialog.transient(root)
    dialog.grab_set()

    # Label oben
    ttk.Label(dialog, text="Bitte lesen Sie die Lizenzbedingungen:", font=("Helvetica", 12)).pack(pady=10)

    # Textbereich in eigenem Frame
    text_frame = ttk.Frame(dialog)
    text_frame.pack(fill="both", expand=True, padx=20, pady=10)

    text_area = ScrolledText(text_frame, autohide=True)
    text_area.pack(fill="both", expand=True)
    text_area.text.insert("1.0", license_text)
    text_area.text.configure(state="disabled")

    # Button-Frame
    button_frame = ttk.Frame(dialog)
    button_frame.pack(pady=10)

    result = {"accepted": None}

    def agree():
        result["accepted"] = True
        dialog.destroy()

    def disagree():
        result["accepted"] = False
        dialog.destroy()

    ttk.Button(button_frame, text="Ich stimme zu", command=agree, bootstyle="success").pack(side="left", padx=10)
    ttk.Button(button_frame, text="Ich lehne ab", command=disagree, bootstyle="danger").pack(side="right", padx=10)

    dialog.wait_window()
    return result["accepted"]

def show_help(root):
    help_text = load_markdown_file(get_resource_path("hilfe.md"))
    show_markdown_window(root, "Hilfe", help_text)


def load_markdown_file(filename):
    if not os.path.exists(filename):
        return f"Datei '{filename}' nicht gefunden."
    with open(filename, "r", encoding="utf-8") as f:
        return markdown.markdown(f.read())


def show_markdown_window(root, title, html_content):
    #window = ttk.Toplevel(root, iconphoto=None)
    if sys.platform == "darwin":
      window = ttk.Toplevel(root)
    else:
       window = ttk.Toplevel(root, iconphoto=None)
    #set_window_icon(window)
    window.title(title)
    window.geometry("600x400")
    html_label = HTMLLabel(window, html=html_content)
    html_label.pack(fill="both", expand=True, padx=10, pady=10)


def show_about():
    # messagebox.showinfo("Über Classload", "Classload\nVersion 1.0\n(c) 2025")
    messagebox.showinfo("Über Classload","Classload\nzum Austausch von Daten mit Jamf\nVersion 0.9\n(c)2025 Christiane Borchel")


def main():
    init_dpi_awareness()
    if sys.platform == "darwin":
      root = ttk.Window(themename="cosmo")
    else:
      root = ttk.Window(themename="cosmo", iconphoto=None)
    root.title("Classload")
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(__file__))
    # icon_path = os.path.join(base_path, "assets", "icon.png")
    #icon_img = tk.PhotoImage(file=icon_path)
    #icon_relpath = os.path.join("assets", "icon.png")  # Pfad zusammensetzen
    if sys.platform == "darwin":
        # macOS → kleineres, sicheres Icon verwenden
        icon_relpath = os.path.join("assets", "icon_small.png")
    else:
        # Windows/Linux → großes Icon mit Alpha
        icon_relpath = os.path.join("assets", "icon.png")

    icon_path = get_resource_path(icon_relpath)  # Pfad für PyInstaller/py2app auflösen
    icon_img = tk.PhotoImage(file=icon_path)
    print("🔍 Icon-Pfad:", icon_path)
    print("📦 Existiert:", os.path.exists(icon_path))
    #root.iconphoto(True, icon_img)
    #root.icon_img = icon_img
    if sys.platform.startswith("win"):
        try:
            icon_path = os.path.join(base_path, "assets", "icon.ico")
            root.iconbitmap(icon_path)
        except Exception as e:
            print(f"Icon konnte nicht gesetzt werden: {e}")
    #set_window_icon(root)

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

    # root.withdraw()  # root bleibt im Hintergrund, aber notwendig für Tkinter


    pruefe_nutzungsart(root)
    #login = JamfLogin(root)
    root.iconphoto(True, icon_img)
    #root.icon_img = icon_img
    root.mainloop()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        log_path = os.path.join(os.path.expanduser("~"), "Desktop", "classload_error.log")


        with open(log_path, "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        raise
