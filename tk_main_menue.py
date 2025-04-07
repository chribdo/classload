from ttkbootstrap.dialogs import Messagebox
from tkinter import filedialog, messagebox, scrolledtext, simpledialog
# --- Lizenzfunktionen & Nutzungsprüfung ---
from datetime import datetime, timedelta
import ttkbootstrap as ttk
import tkinter as tk
from ttkbootstrap.dialogs import *
from ttkbootstrap.constants import *
from tkinter.messagebox import askokcancel
import json
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.scrolled import ScrolledText
from jamfscripts import *
import os, sys, getpass
import threading
import time
JAMF_URL=""
TOKEN=""
ZUSTIMMUNGSDATEI = os.path.join(os.getcwd(), "zustimmung.json")
NUTZUNGSDATEI = os.path.join(os.getcwd(), "nutzung.json")





def lade_nutzungsinfo():
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
            Messagebox.ok(title="Testzeitraum abgelaufen", message="Die 7-Tage-Testversion ist abgelaufen. Bitte kontaktieren Sie den Entwickler für eine Lizenz.", alert=True)
            sys.exit()
        else:
            Messagebox.ok(title="Testversion", message=f"Testversion aktiv. Noch {verbleibend.days + 1} Tage verfügbar.", alert=False)

def zeige_lizenz():
    if not os.path.exists("LICENSE.txt"):
        Messagebox.ok(title="Lizenz", message="LICENSE.txt nicht gefunden.", alert=False)
        return
    lizfenster = tk.Toplevel()
    lizfenster.title("Lizenz")
    lizfenster.geometry("600x500")
    textfeld = scrolledtext.ScrolledText(lizfenster, wrap="word")
    with open("LICENSE.txt", "r", encoding="utf-8") as f:
        textfeld.insert("1.0", f.read())
    textfeld.config(state="disabled")
    textfeld.pack(fill="both", expand=True)


def zeige_nutzungsdialog():
    auswahlfenster = tk.Toplevel()
    auswahlfenster.title("Nutzungsart wählen")
    auswahlfenster.geometry("400x200")
    auswahlfenster.grab_set()
    auswahlfenster.resizable(False, False)

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






class JamfLogin:
    def __init__(self, root):
        self.root = root

        # Menüeintrag „Lizenz anzeigen“ ergänzen
        menubar = tk.Menu(root)
        hilfe_menu = tk.Menu(menubar, tearoff=0)
        hilfe_menu.add_command(label="Lizenz anzeigen", command=zeige_lizenz)
        menubar.add_cascade(label="Hilfe", menu=hilfe_menu)
        root.config(menu=menubar)
        # self.root.withdraw()  # Hauptfenster verbergen

        self.login_window = ttk.Toplevel(root)
        self.login_window.title("JAMF Login")
        self.login_window.geometry("600x300")
        self.login_window.resizable(False, False)
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

    def on_close(self):
        LOGGER.info("Fenster wird geschlossen. Programm wird beendet.")
        sys.exit()  # Beendet das ganze Skript

    def validate_login(self):
        global JAMF_URL, TOKEN

        JAMF_URL = self.url_entry.get()
        username = self.username_entry.get()
        #password = self.password_entry.get()

        if not JAMF_URL or not username or not self.password_entry.get():
            #messagebox.showwarning("Fehler", "Alle Felder müssen ausgefüllt werden!")
            Messagebox.ok(
                title="Alles ausgefüllt?",
                message="Alle Felder müssen ausgefüllt werden!.",
                alert=True,
            )

            return

        encrypted_password = get_cipher().encrypt(self.password_entry.get().encode())
        TOKEN = get_auth_token(JAMF_URL, username, encrypted_password)


        if TOKEN == "":
            # Messagebox.ok(title="Login fehlgeschlagen", "Bitte überprüfen Sie die Zugangsdaten.", alert=True)
            Messagebox.ok(
                title="Login fehlgeschlagen",
                message="Bitte überprüfen Sie die Zugangsdaten.",
                alert=True
            )
        else:
            # Messagebox.ok(title="Erfolg", "Login erfolgreich!", alert=False)
            #Messagebox.ok(
            #    title="Erfolg",
            #    message="Login erfolgreich.",
            # )
            initialisiere(JAMF_URL, TOKEN)
            self.login_window.destroy()
            app1 = KlassenUploaderApp(self.login_window.master)
            self.root.deiconify()


class KlassenUploaderApp:
    def __init__(self, root):
        self.root = root

        # Menüeintrag „Lizenz anzeigen“ ergänzen
        menubar = tk.Menu(root)
        hilfe_menu = tk.Menu(menubar, tearoff=0)
        hilfe_menu.add_command(label="Lizenz anzeigen", command=zeige_lizenz)
        menubar.add_cascade(label="Hilfe", menu=hilfe_menu)
        root.config(menu=menubar)
        self.root.title("Classload")
        self.root.geometry("1200x400")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        button_frame = ttk.Frame(root)
        button_frame.pack(padx=10, pady=10)

        # Buttons
        self.btn_konfiguration = ttk.Button(button_frame, text="Konfiguration", command=self.konfigurieren)
        self.btn_sus_ipads_zuordnen = ttk.Button(button_frame, text="Schüler_innen-iPads zuordnen", command=self.schueler_ipads_zuordnen)
        self.btn_lehrer_ipads_zuordnen = ttk.Button(button_frame, text="Lehrkräfte-iPads zuordnen", command=self.lehrer_ipads_zuordnen)
        self.btn_it_nummern_hochladen = ttk.Button(button_frame, text="IT-Nummern/Asset-Tags hochladen", command=self.it_nummern_hochladen)
        self.btn_upload = ttk.Button(button_frame, text="Klassen-Upload", command=self.klassen_upload)
        self.btn_single_group_upload = ttk.Button(button_frame, text="Benutzergruppe zu existierender Klasse erzeugen", command=self.single_group_upload)
        self.btn_group_upload = ttk.Button(button_frame, text="Zu jeder Klasse eine Benutzergruppe erzeugen", command=self.group_upload)
        self.btn_gruppen_loeschen = ttk.Button(button_frame, text="Gruppen löschen", command=self.gruppen_loeschen)
        self.btn_loeschen = ttk.Button(button_frame, text="Klassen löschen", command=self.klassen_loeschen)

        self.btn_del_users = ttk.Button(button_frame, text="Benutzer ohne Mobilgerät löschen", command=self.delete_users_wo_md)

        self.btn_konfiguration.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.btn_sus_ipads_zuordnen.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.btn_lehrer_ipads_zuordnen.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        self.btn_it_nummern_hochladen.grid(row=3, column=0, padx=5, pady=5, sticky="ew")
        self.btn_upload.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.btn_single_group_upload.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.btn_group_upload.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.btn_loeschen.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        self.btn_gruppen_loeschen.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        self.btn_del_users.grid(row=4, column=0, padx=5, pady=5, sticky="ew")


        """
        # Buttons platzieren
        self.btn_konfiguration.pack(pady=5)
        self.btn_sus_ipads_zuordnen.pack(pady=5)
        self.btn_lehrer_ipads_zuordnen.pack(pady=5)
        self.btn_it_nummern_hochladen.pack(pady=5)
        self.btn_upload.pack(pady=5)
        self.btn_single_group_upload.pack(pady=5)
        self.btn_group_upload.pack(pady=5)
        self.btn_loeschen.pack(pady=5)
        self.btn_gruppen_loeschen.pack(pady=5)

        self.btn_del_users.pack(pady=5)
        """
        # Textfeld für Log-Ausgabe
        self.text_log = scrolledtext.ScrolledText(root, height=20, width=80, state=tk.DISABLED, wrap=tk.WORD)
        self.text_log.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.update_log()

    def on_close(self):
        LOGGER.info("Fenster wird geschlossen. Programm wird beendet.")
        sys.exit()  # Beendet das ganze Skript

    def popup_closed(self, window):
        window.destroy()  # Fenster schließen
        self.root.deiconify()  # Hauptfenster wieder anzeigen

    def konfigurieren(self):
        def speichern():
            set_config_value("TEACHER_GROUP_NAME", entry_teachergroup.get())
            set_config_value("SITE_ID", entry_site_id.get())
            set_config_value("OUTPUT_FILE_CLASSES", entry_output_classes.get())
            set_config_value("OUTPUT_FILE_STUDENTS", entry_output_sus.get())
            set_config_value("POSTFIX", entry_postfix.get())
            set_config_value("TEACHER_POSTFIX", entry_lehrkraefte_postfix.get())
            #Messagebox.ok(title="Eingaben gespeichert", "Eingaben gespeichert", alert=False)
            Messagebox.ok(
                title="Gespeichert?",
                message="Eingaben gespeichert.",
            )
            popup.destroy()
            self.root.deiconify()



        # Popup-Fenster
        popup = ttk.Toplevel()
        popup.protocol("WM_DELETE_WINDOW", lambda: self.popup_closed(popup))
        self.root.withdraw()
        popup.title("Formular")
        popup.geometry("700x250")

        # Labels und Eingabefelder
        ttk.Label(popup, text="Statische Benutzergruppe aller Lehrkräfte in JAMF:").grid(row=0, column=0, sticky='e', padx=5, pady=2)
        entry_teachergroup = ttk.Entry(popup)
        tg=config.get_config_value("TEACHER_GROUP_NAME")
        entry_teachergroup.insert(0, tg)
        entry_teachergroup.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(popup, text="SITE-ID:").grid(row=1, column=0, sticky='e', padx=5, pady=2)
        entry_site_id = ttk.Entry(popup)
        sid = get_config_value("SITE_ID")
        entry_site_id.insert(0, sid)
        entry_site_id.grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(popup,  text="Pfad zur Ausgabe aktualisierter Schüler:").grid(row=2, column=0, sticky='e', padx=5, pady=2)
        entry_output_sus = ttk.Entry(popup)
        ofs = get_config_value("OUTPUT_FILE_STUDENTS")
        entry_output_sus.insert(0, ofs)
        entry_output_sus.grid(row=2, column=1, padx=5, pady=2)

        ttk.Label(popup, text="Pfad zur Ausgabe der Classroom-Klassen-Daten:").grid(row=3, column=0, sticky='e', padx=5, pady=2)
        entry_output_classes = ttk.Entry(popup)
        ofc = get_config_value("OUTPUT_FILE_CLASSES")
        entry_output_classes.insert(0, ofc)
        entry_output_classes.grid(row=3, column=1, padx=5, pady=2)

        ttk.Label(popup, text="Mögliches Postfix für JAMF-Schüler-Benutzer ggf. mit Leerzeichen:").grid(row=4, column=0, sticky='e', padx=5, pady=2)
        entry_postfix = ttk.Entry(popup)
        pf = get_config_value("POSTFIX")
        entry_postfix.insert(0, pf)
        entry_postfix.grid(row=4, column=1, padx=5, pady=2)

        ttk.Label(popup, text="Lehrkräfte-POSTFIX:").grid(row=5, column=0, sticky='e', padx=5, pady=2)
        entry_lehrkraefte_postfix = ttk.Entry(popup)
        pf = get_config_value("TEACHER_POSTFIX")
        entry_lehrkraefte_postfix.insert(0, pf)
        entry_lehrkraefte_postfix.grid(row=5, column=1, padx=5, pady=2)

        # Speichern-Button
        ttk.Button(popup, text="Speichern", command=speichern).grid(row=6, column=0, columnspan=2, pady=10)

    def klassen_upload(self):
        """Wählt eine Datei aus und gibt ein Präfix ein, bevor eine Funktion ausgeführt wird."""
        # Präfix eingeben
        popup = ttk.Toplevel(self.root)
        popup.title("Upload-Einstellungen")
        popup.geometry("600x300")
        ttk.Label(popup, text="Präfix für neue Klassen:").pack(pady=5)
        prefix_entry = ttk.Entry(popup)
        prefix_entry.pack(pady=5)
        ttk.Label(popup, text="Name der statischen JAMF-Lehrer-Benutzergruppe:").pack(pady=5)
        teachergroup_entry = ttk.Entry(popup)
        teachergroup_entry.insert(0, get_config_value("TEACHER_GROUP_NAME"))
        teachergroup_entry.pack(pady=5)
        praefix=""
        teachergroup=""
        def on_submit():
            praefix = prefix_entry.get()
            teachergroup = teachergroup_entry.get()
            set_config_value("TEACHER_GROUP_NAME", teachergroup)
            if not praefix or not teachergroup:
                #Messagebox.ok(title="Fehler", "Die Werte dürfen nicht leer sein!", alert=True)
                Messagebox.ok(
                    title="Fehler",
                    message="Die Werte dürfen nicht leer sein.",
                    alert=True
                )
                return
            popup.destroy()

        ttk.Button(popup, text="Bestätigen", command=on_submit).pack(pady=10)
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

    def schueler_ipads_zuordnen(self):
        """Upload mit Zuordnung der Schülernamen zu Seriennummern gemäß csv."""
        #Messagebox.ok(title="Datei auswählen","Bitte csv mit 3 Spalten auswählen: Vorname, Nachname, Seriennummer", alert=False)
        Messagebox.ok(
            title="Datei auswählen",
            message="Bitte csv mit 3 Spalten auswählen: Vorname, Nachname, Seriennummer.",
        )
        # Datei auswählen

        dateipfad = filedialog.askopenfilename(title="CSV-Auswahl",
                                               filetypes=(("CSV-Dateien", "*.csv"), ("Alle Dateien", "*.*")))
        if not dateipfad:
            LOGGER.error("❌ Kein Dateipfad ausgewählt!")
            return
        else:
            threading.Thread(target=schueler_ipads_aktualisieren, args=(JAMF_URL, TOKEN, dateipfad), daemon=True).start()

    def lehrer_ipads_zuordnen(self):
        """Upload mit Zuordnung der Schülernamen zu Seriennummern gemäß csv."""
        #Messagebox.ok(title="Datei auswählen", "Bitte csv mit 4 Spalten auswählen: Vorname, Nachname, eindeutiges Kürzel, Seriennummer", alert=False)
        Messagebox.ok(
            title="Datei auswählen",
            message="Bitte csv mit 4 Spalten auswählen: Vorname, Nachname, eindeutiges Kürzel, Seriennummer.",
            alert=True
        )
        # Datei auswählen
        dateipfad = filedialog.askopenfilename(title="CSV-Auswahl",
                                               filetypes=(("CSV-Dateien", "*.csv"), ("Alle Dateien", "*.*")))
        if not dateipfad:
            LOGGER.error("❌ Kein Dateipfad ausgewählt!")
            return
        else:
            threading.Thread(target=lehrer_ipads_aktualisieren, args=(JAMF_URL, TOKEN, dateipfad),
                             daemon=True).start()

    def it_nummern_hochladen(self):
        """Upload mit Zuordnung der Schülernamen zu Seriennummern gemäß csv."""
        #Messagebox.ok(title="Datei auswählen", "Bitte csv mit 2 Spalten auswählen: Asset Tag (IT-Nummer, alert=False), Seriennummer")
        Messagebox.ok(
            title="Datei auswählen",
            message="Bitte csv mit 2 Spalten auswählen: Asset Tag (IT-Nummer); Seriennummer",
        )
        #antwort = askokcancel("Datei auswählen","CSV auswählen")
        # Datei auswählen

        dateipfad = filedialog.askopenfilename(title="CSV auswählen",
                                               filetypes=(("CSV-Dateien", "*.csv"), ("Alle Dateien", "*.*")))
        if not dateipfad:
            LOGGER.error("❌ Kein Dateipfad ausgewählt!")
            return
        else:
            threading.Thread(target=it_nummern_hochladen, args=(JAMF_URL, TOKEN, dateipfad), daemon=True).start()

    def group_upload(self):
        """Wählt eine Datei aus und gibt ein Präfix ein, bevor eine Funktion ausgeführt wird."""
        # Präfix eingeben
        popup = ttk.Toplevel(self.root)
        popup.title("Upload-Einstellungen")
        popup.geometry("600x300")
        ttk.Label(popup, text="Präfix für neue Statische Benutzergruppen:").pack(pady=5)
        prefix_entry = ttk.Entry(popup)
        prefix_entry.pack(pady=5)
        ttk.Label(popup, text="Name der statischen JAMF-Lehrer-Benutzergruppe:").pack(pady=5)
        teachergroup_entry = ttk.Entry(popup)
        teachergroup_entry.insert(0, get_config_value("TEACHER_GROUP_NAME"))
        teachergroup_entry.pack(pady=5)
        praefix=""
        teachergroup=""
        def on_submit():
            praefix = prefix_entry.get()
            teachergroup = teachergroup_entry.get()
            set_config_value("TEACHER_GROUP_NAME", teachergroup)
            if not praefix or not teachergroup:
                #Messagebox.ok(title="Fehler", "Die Werte dürfen nicht leer sein!", alert=True)
                Messagebox.ok(
                    title="Fehler",
                    message="Die Werte dürfen nicht leer sein.",
                    alert=True
                )
                return
            popup.destroy()

        ttk.Button(popup, text="Bestätigen", command=on_submit).pack(pady=10)
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
            threading.Thread(target=self.gruppen_upload_ausfuehren, args=(dateipfad, praefix, teachergroup), daemon=True).start()



    def klassen_loeschen(self):
        # Präfix eingeben
        popup = ttk.Toplevel(self.root)
        popup.title("Klassen-Präfix")
        popup.geometry("600x300")
        ttk.Label(popup, text="Bitte das Klassen-Präfix, der Klassen eingeben, die gelöscht werden sollen: ").pack(pady=5)
        prefix_entry = ttk.Entry(popup)
        prefix_entry.pack(pady=5)

        def on_submit():
            del_praefix = prefix_entry.get()
            print(del_praefix);
            if not del_praefix:
                #Messagebox.ok(title="Fehler", "Präfix darf nicht leer sein!", alert=True)
                Messagebox.ok(
                    title="Fehler",
                    message="Präfix darf nicht leer sein.",
                    alert=True
                )
                return
            popup.destroy()
            threading.Thread(target=self.klassen_loeschen_ausfuehren, args=(del_praefix,), daemon=True).start()

        ttk.Button(popup, text="Bestätigen", command=on_submit).pack(pady=10)

    def single_group_upload(self):
        popup = ttk.Toplevel(self.root)
        popup.title("Klassen-Namen eingeben")
        popup.geometry("800x200")
        ttk.Label(popup, text="Bitte den Namen, der Klassen eingeben, zu der eine statische Benutzergruppe angelegt werden soll: ").pack(pady=5)
        class_entry = ttk.Entry(popup)
        class_entry.pack(pady=5)

        def on_submit():
            classname = class_entry.get()
            print(classname);
            if not classname:
                #Messagebox.ok(title="Fehler", "Bitte alles ausfüllen!", alert=True)
                Messagebox.ok(
                    title="Alles ausgefüllt?",
                    message="Bitte alles ausfüllen.",
                    alert=True
                )
                return
            popup.destroy()
            threading.Thread(target=create_single_user_group, args=(JAMF_URL, TOKEN, classname), daemon=True).start()

        ttk.Button(popup, text="Bestätigen", command=on_submit).pack(pady=10)

    def gruppen_loeschen(self):
        # Präfix eingeben
        popup = ttk.Toplevel(self.root)
        popup.title("Gruppen-Präfix")
        popup.geometry("600x300")
        ttk.Label(popup, text="Bitte das Gruppen-Präfix, der Benutzergruppen eingeben, die gelöscht werden sollen: ").pack(
            pady=5)
        prefix_entry = ttk.Entry(popup)
        prefix_entry.pack(pady=5)

        def on_submit():
            del_praefix = prefix_entry.get()
            print(del_praefix);
            if not del_praefix:
                # Messagebox.ok(title="Fehler", "Präfix darf nicht leer sein!", alert=True)
                Messagebox.ok(
                    title="Fehler",
                    message="Präfix darf nicht leer sein.",
                    alert=True
                )
                return
            popup.destroy()
            threading.Thread(target=self.gruppen_loeschen_ausfuehren, args=(del_praefix,), daemon=True).start()

        ttk.Button(popup, text="Bestätigen", command=on_submit).pack(pady=10)

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

    """
   # Probierversion klappt nicht richtig
    def klassen_loeschen_ausfuehren(self, del_praefix):
        def frage():
            antwort = Messagebox.yesno(
                title="Klassen löschen nach Präfix",
                message=f"Alle Klassen in JAMF mit dem Präfix {del_praefix} werden gelöscht.",
                alert=True,
                parent=self.root  # Nur wenn self.root wirklich dein sichtbares Fenster ist
            )

            if antwort == "Yes":
                # Langer Prozess in separatem Thread
                threading.Thread(
                    target=lambda: loesche_klassen_mit_prefix(JAMF_URL, TOKEN, del_praefix),
                    daemon=True
                ).start()
            else:
                print("Abgebrochen")

        # Dialog sicher im Hauptthread ausführen
        self.root.after(0, frage)
    """
    def gruppen_loeschen_ausfuehren(self, del_praefix):

        antwort = messagebox.askokcancel("Gruppen löschen nach Präfix", f"Alle Benutzergruppen in JAMF mit dem Präfix {del_praefix} werden gelöscht.")

        if antwort:
            loesche_usergroups_mit_prefix(JAMF_URL, TOKEN, del_praefix)
        else:
            return

    def klassenupload_ausfuehren(self, dateipfad, praefix, teachergroupname):

        # print(teachergroupname)
        SITE_ID = get_config_value("SITE_ID")
        OUTPUT_FILE_CLASSES = get_config_value("OUTPUT_FILE_CLASSES")
        OUTPUT_FILE_STUDENTS = get_config_value("OUTPUT_FILE_STUDENTS")
        POSTFIX = get_config_value("POSTFIX")
        big_merge(JAMF_URL, TOKEN, dateipfad, SITE_ID, teachergroupname, praefix, OUTPUT_FILE_STUDENTS,
                  OUTPUT_FILE_CLASSES, POSTFIX)

    def gruppen_upload_ausfuehren(self, dateipfad, praefix, teachergroupname):

        # print(teachergroupname)
        SITE_ID = get_config_value("SITE_ID")
        OUTPUT_FILE_CLASSES = get_config_value("OUTPUT_FILE_CLASSES")
        OUTPUT_FILE_STUDENTS = get_config_value("OUTPUT_FILE_STUDENTS")
        POSTFIX = get_config_value("POSTFIX")
        create_user_groups(JAMF_URL, TOKEN, dateipfad, SITE_ID, teachergroupname, praefix, OUTPUT_FILE_STUDENTS,
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


def zeige_about_dialog():
    about = tk.Toplevel()
    about.title("Über dieses Tool")
    about.geometry("400x200")
    about.resizable(False, False)

    frame = ttk.Frame(about, padding=20)
    frame.pack(fill="both", expand=True)

    label = ttk.Label(frame, text="macOS Tool für JAMF-Interaktionen\nVersion 1.0.0\n© 2025 von Dir", justify="center", font=("Helvetica", 12))
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
            with open("LICENSE.txt", "r", encoding="utf-8") as f:
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


def main():
    root = ttk.Window(themename="cosmo")
    #root.withdraw()
    #root.update()
    if not zustimmung_bereits_erfolgt():
        if not show_license_dialog(root):
            return
        speichere_zustimmung()

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
        with open("/tmp/classload_error.log", "w") as f:
            f.write(traceback.format_exc())
        raise


