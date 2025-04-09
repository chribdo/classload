# tk_jamf_login.py
from tk_klassen_uploader_app import KlassenUploaderApp
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox
from jamfscripts import *
import sys


class JamfLogin:
    def __init__(self, root):
        self.root = root

        self.login_window = ttk.Toplevel(root)
        self.login_window.title("JAMF Login")
        self.login_window.geometry("600x350")
        self.login_window.resizable(False, True)
        self.login_window.update_idletasks()
        self.login_window.minsize(self.login_window.winfo_width(), self.login_window.winfo_height())
        self.login_window.protocol("WM_DELETE_WINDOW", self.on_close)

        ttk.Label(self.login_window, text="JAMF-URL:").pack(pady=5)
        self.url_entry = ttk.Entry(self.login_window, width=40)
        self.url_entry.insert(0, "https://dosys.jamfcloud.com")
        self.url_entry.pack()

        ttk.Label(self.login_window, text="Benutzername:").pack(pady=5)
        self.username_entry = ttk.Entry(self.login_window, width=40)
        self.username_entry.pack()

        ttk.Label(self.login_window, text="Passwort:").pack(pady=5)
        self.password_entry = ttk.Entry(self.login_window, width=40, show="*")
        self.password_entry.pack()

        self.login_button = ttk.Button(self.login_window, text="Login", command=self.validate_login)
        self.login_button.pack(pady=10)

    def show_about(self):
        messagebox.showinfo("Über Classload",
                            "Classload\nzum Austausch von Daten mit Jamf\nVersion 0.9\n(c)2025 Christiane Borchel")
        #messagebox.showinfo("Über Classload", "Classload\nVersion 1.0\n(c) 2025")

    def on_close(self):
        LOGGER.info("Fenster wird geschlossen. Programm wird beendet.")
        sys.exit()  # Beendet das ganze Skript

    def validate_login(self):
        global JAMF_URL, TOKEN

        JAMF_URL = self.url_entry.get()
        username = self.username_entry.get()
        # password = self.password_entry.get()

        if not JAMF_URL or not username or not self.password_entry.get():
            # messagebox.showwarning("Fehler", "Alle Felder müssen ausgefüllt werden!")
            Messagebox.ok(
                title="Alles ausgefüllt?",
                message="Alle Felder müssen ausgefüllt werden!.",
                alert=True,
                parent= self.login_window
            )

            return

        encrypted_password = get_cipher().encrypt(self.password_entry.get().encode())
        TOKEN = get_auth_token(JAMF_URL, username, encrypted_password)

        if TOKEN == "":
            # Messagebox.ok(title="Login fehlgeschlagen", "Bitte überprüfen Sie die Zugangsdaten.", alert=True)
            Messagebox.ok(
                title="Login fehlgeschlagen",
                message="Bitte überprüfen Sie die Zugangsdaten.",
                alert=True,
                parent=self.login_window            )
        else:
            # Messagebox.ok(title="Erfolg", "Login erfolgreich!", alert=False)
            # Messagebox.ok(
            #    title="Erfolg",
            #    message="Login erfolgreich.",
            # )
            initialisiere(JAMF_URL, TOKEN)
            self.login_window.destroy()
            #app1 = KlassenUploaderApp(self.login_window.master, JAMF_URL, TOKEN)
            app1 = KlassenUploaderApp(self.login_window.master, JAMF_URL, TOKEN)
            self.root.deiconify()
