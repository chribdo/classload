import tkinter as tk

from tkinter import messagebox, Toplevel, scrolledtext, simpledialog, filedialog
from tkinter.messagebox import askokcancel

from jamfscripts import *
import os, sys, getpass
import threading
import time

JAMF_URL=""
TOKEN=""

class JamfLogin:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()  # Hauptfenster verbergen

        self.login_window = tk.Toplevel(root)
        self.login_window.title("JAMF Login")
        self.login_window.geometry("600x300")
        self.login_window.resizable(False, False)
        self.login_window.protocol("WM_DELETE_WINDOW", self.on_close)

        tk.Label(self.login_window, text="JAMF-URL:").pack(pady=5)
        self.url_entry = tk.Entry(self.login_window, width=40)
        self.url_entry.insert(0, "https://dosys.jamfcloud.com")
        self.url_entry.pack()

        tk.Label(self.login_window, text="Benutzername:").pack(pady=5)
        self.username_entry = tk.Entry(self.login_window, width=40)
        self.username_entry.pack()

        tk.Label(self.login_window, text="Passwort:").pack(pady=5)
        self.password_entry = tk.Entry(self.login_window, width=40, show="*")
        self.password_entry.pack()

        self.login_button = tk.Button(self.login_window, text="Login", command=self.validate_login)
        self.login_button.pack(pady=10)

    def on_close(self):
        LOGGER.info("Fenster wird geschlossen. Programm wird beendet.")
        self.root.destroy()
        sys.exit()  # Beendet das ganze Skript

    def validate_login(self):
        global JAMF_URL, TOKEN

        JAMF_URL = self.url_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not JAMF_URL or not username or not password:
            messagebox.showwarning("Fehler", "Alle Felder müssen ausgefüllt werden!")
            return

        encrypted_password = get_cipher().encrypt(password.encode())
        TOKEN = get_auth_token(JAMF_URL, username, encrypted_password)


        if TOKEN == "":
            messagebox.showerror("Login fehlgeschlagen", "Bitte überprüfen Sie die Zugangsdaten.")
        else:
            # messagebox.showinfo("Erfolg", "Login erfolgreich!")
            initialisiere(JAMF_URL, TOKEN)
            self.login_window.destroy()
            app1 = KlassenUploaderApp(root)
            self.root.deiconify()


class KlassenUploaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("JAMF Schulverwaltung")
        self.root.geometry("1200x400")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Buttons
        self.btn_konfiguration = tk.Button(root, text="Konfiguration", command=self.konfigurieren)
        self.btn_upload = tk.Button(root, text="Klassen-Upload", command=self.klassen_upload)
        self.btn_loeschen = tk.Button(root, text="Klassen löschen", command=self.klassen_loeschen)
        self.btn_del_users = tk.Button(root, text="Benutzer ohne Mobilgerät löschen", command=self.delete_users_wo_md)

        # Buttons platzieren
        self.btn_konfiguration.pack(pady=5)
        self.btn_upload.pack(pady=5)
        self.btn_loeschen.pack(pady=5)
        self.btn_del_users.pack(pady=5)

        # Textfeld für Log-Ausgabe
        self.text_log = scrolledtext.ScrolledText(root, height=20, width=80, state=tk.DISABLED, wrap=tk.WORD)
        self.text_log.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.update_log()

    def on_close(self):
        LOGGER.info("Fenster wird geschlossen. Programm wird beendet.")
        self.root.destroy()
        sys.exit()  # Beendet das ganze Skript

    def konfigurieren(self):
        def speichern():
            set_config_value("TEACHER_GROUP_NAME", entry_teachergroup.get())
            set_config_value("SITE_ID", entry_site_id.get())
            set_config_value("OUTPUT_FILE_CLASSES", entry_output_classes.get())
            set_config_value("OUTPUT_FILE_STUDENTS", entry_output_sus.get())
            set_config_value("POSTFIX", entry_postfix.get())
            messagebox.showinfo("Eingaben gespeichert", "Eingaben gespeichert")
            popup.destroy()



        # Hauptfenster
        root = tk.Tk()
        root.withdraw()  # Hauptfenster ausblenden

        # Popup-Fenster
        popup = tk.Toplevel()
        popup.title("Formular")
        popup.geometry("700x250")

        # Labels und Eingabefelder
        tk.Label(popup, text="Statische Benutzergruppe aller Lehrkräfte in JAMF:").grid(row=0, column=0, sticky='e', padx=5, pady=2)
        entry_teachergroup = tk.Entry(popup)
        tg=config.get_config_value("TEACHER_GROUP_NAME")
        entry_teachergroup.insert(0, tg)
        entry_teachergroup.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(popup, text="SITE-ID:").grid(row=1, column=0, sticky='e', padx=5, pady=2)
        entry_site_id = tk.Entry(popup)
        sid = get_config_value("SITE_ID")
        entry_site_id.insert(0, sid)
        entry_site_id.grid(row=1, column=1, padx=5, pady=2)

        tk.Label(popup,  text="Pfad zur Ausgabe aktualisierter Schüler:").grid(row=2, column=0, sticky='e', padx=5, pady=2)
        entry_output_sus = tk.Entry(popup)
        ofs = get_config_value("OUTPUT_FILE_STUDENTS")
        entry_output_sus.insert(0, ofs)
        entry_output_sus.grid(row=2, column=1, padx=5, pady=2)

        tk.Label(popup, text="Pfad zur Ausgabe der Classroom-Klassen-Daten:").grid(row=3, column=0, sticky='e', padx=5, pady=2)
        entry_output_classes = tk.Entry(popup)
        ofc = get_config_value("OUTPUT_FILE_CLASSES")
        entry_output_classes.insert(0, ofc)
        entry_output_classes.grid(row=3, column=1, padx=5, pady=2)

        tk.Label(popup, text="Mögliches Postfix für JAMF-Schüler-Benutzer ggf. mit Leerzeichen:").grid(row=4, column=0, sticky='e', padx=5, pady=2)
        entry_postfix = tk.Entry(popup)
        pf = get_config_value("POSTFIX")
        entry_postfix.insert(0, pf)
        entry_postfix.grid(row=4, column=1, padx=5, pady=2)

        # Speichern-Button
        tk.Button(popup, text="Speichern", command=speichern).grid(row=6, column=0, columnspan=2, pady=10)

    def klassen_upload(self):
        """Wählt eine Datei aus und gibt ein Präfix ein, bevor eine Funktion ausgeführt wird."""
        # Präfix eingeben
        popup = tk.Toplevel(self.root)
        popup.title("Upload-Einstellungen")
        popup.geometry("600x300")
        tk.Label(popup, text="Präfix für neue Klassen:").pack(pady=5)
        prefix_entry = tk.Entry(popup)
        prefix_entry.pack(pady=5)
        tk.Label(popup, text="Name der statischen JAMF-Lehrer-Benutzergruppe:").pack(pady=5)
        teachergroup_entry = tk.Entry(popup)
        teachergroup_entry.insert(0, get_config_value("TEACHER_GROUP_NAME"))
        teachergroup_entry.pack(pady=5)
        praefix=""
        teachergroup=""
        def on_submit():
            praefix = prefix_entry.get()
            teachergroup = teachergroup_entry.get()
            set_config_value("TEACHER_GROUP_NAME", teachergroup)
            if not praefix or not teachergroup:
                messagebox.showerror("Fehler", "Die Werte dürfen nicht leer sein!")
                return
            popup.destroy()

        tk.Button(popup, text="Bestätigen", command=on_submit).pack(pady=10)
        popup.wait_window()
        # Datei auswählen
        dateipfad = config.get_config_value("INPUT_FILENAME")
        dateipfad = filedialog.askopenfilename(initialdir=dateipfad, title="Bitte iServ-Schüler-csv auswählen",
                                               filetypes=(("CSV-Dateien", "*.csv"), ("Alle Dateien", "*.*")))
        if not dateipfad:
            LOGGER.error("❌ Kein Dateipfad ausgewählt!")
            return
        else:
            set_config_value("INPUT_FILE_NAME", dateipfad)
            teachergroup=get_config_value("TEACHER_GROUP_NAME")
            threading.Thread(target=self.klassenupload_ausfuehren, args=(dateipfad, praefix, teachergroup), daemon=True).start()

    def klassen_loeschen(self):
        # Präfix eingeben
        popup = tk.Toplevel(self.root)
        popup.title("Klassen-Präfix")
        popup.geometry("600x300")
        tk.Label(popup, text="Bitte das Klassen-Präfix, der Klassen eingeben, die gelöscht werden sollen: ").pack(pady=5)
        prefix_entry = tk.Entry(popup)
        prefix_entry.pack(pady=5)

        def on_submit():
            del_praefix = prefix_entry.get()
            print(del_praefix);
            if not del_praefix:
                messagebox.showerror("Fehler", "Präfix darf nicht leer sein!")
                return
            popup.destroy()
            threading.Thread(target=self.klassen_loeschen_ausfuehren, args=(del_praefix,), daemon=True).start()

        tk.Button(popup, text="Bestätigen", command=on_submit).pack(pady=10)

    def delete_users_wo_md(self):
        ok_del=askokcancel("Bestätigen", "Alle Benutzer ohne Mobilgerät werden gelöscht (Lehrkräfte ausgenommen).")
        if ok_del:
            threading.Thread(target=delete_users_without_devices, args=(JAMF_URL,TOKEN), daemon=True).start()
        else:
            return


    def klassen_loeschen_ausfuehren(self, del_praefix):

        antwort = messagebox.askokcancel("Klassen löschen nach Präfix", f"Alle Klassen in JAMF mit dem Präfix {del_praefix} werden gelöscht.")
        if antwort:
            loesche_klassen_mit_prefix(JAMF_URL, TOKEN, del_praefix)
        else:
            return

    def klassenupload_ausfuehren(self, dateipfad, praefix, teachergroupname):
        """Simuliert eine Datei-Verarbeitung mit Konsolenausgaben."""
        print(teachergroupname)
        SITE_ID = get_config_value("SITE_ID")
        OUTPUT_FILE_CLASSES = get_config_value("OUTPUT_FILE_CLASSES")
        OUTPUT_FILE_STUDENTS = get_config_value("OUTPUT_FILE_STUDENTS")
        POSTFIX = get_config_value("POSTFIX")
        big_merge(JAMF_URL, TOKEN, dateipfad, SITE_ID, teachergroupname, praefix, OUTPUT_FILE_STUDENTS,
                  OUTPUT_FILE_CLASSES, POSTFIX)


    def update_log(self):
        """Liest die Log-Datei aus und aktualisiert das Log-Textfeld."""
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r", encoding="utf-8") as log_file:
                log_inhalt = log_file.read()

            self.text_log.config(state=tk.NORMAL)
            self.text_log.delete(1.0, tk.END)  # Vorherigen Inhalt löschen
            self.text_log.insert(tk.END, log_inhalt)
            self.text_log.config(state=tk.DISABLED)
            self.text_log.yview(tk.END)  # Automatisch nach unten scrollen

        # Regelmäßig aktualisieren (alle 1000ms = 1 Sekunde)
        self.root.after(1000, self.update_log)



# Hauptfenster erstellen
root = tk.Tk()
root.withdraw()
app = JamfLogin(root)


root.mainloop()

root.deiconify()

