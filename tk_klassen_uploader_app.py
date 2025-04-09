from tkinter import filedialog, messagebox, scrolledtext
from tkhtmlview import HTMLLabel
from tkinter.messagebox import askokcancel
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox

from jamfscripts import *
import os, sys, markdown
import threading


class KlassenUploaderApp:
    def __init__(self, root, JAMF_URL, TOKEN):
        self.JAMF_URL = JAMF_URL
        self.TOKEN = TOKEN
        self.root = root
        self.root.title("Classload")
        self.root.geometry("1200x400")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        button_frame = ttk.Frame(root)
        button_frame.pack(padx=10, pady=10)

        # Buttons
        self.btn_konfiguration = ttk.Button(button_frame, text="Konfiguration", command=self.konfigurieren)
        self.btn_sus_ipads_zuordnen = ttk.Button(button_frame, text="Schüler_innen-iPads zuordnen",
                                                 command=self.schueler_ipads_zuordnen)
        self.btn_lehrer_ipads_zuordnen = ttk.Button(button_frame, text="Lehrkräfte-iPads zuordnen",
                                                    command=self.lehrer_ipads_zuordnen)
        self.btn_it_nummern_hochladen = ttk.Button(button_frame, text="IT-Nummern/Asset-Tags hochladen",
                                                   command=self.it_nummern_hochladen)
        self.btn_upload = ttk.Button(button_frame, text="Klassen-Upload", command=self.klassen_upload)
        self.btn_single_group_upload = ttk.Button(button_frame, text="Benutzergruppe zu existierender Klasse erzeugen",
                                                  command=self.single_group_upload)
        self.btn_group_upload = ttk.Button(button_frame, text="Zu jeder Klasse eine Benutzergruppe erzeugen",
                                           command=self.group_upload)
        self.btn_gruppen_loeschen = ttk.Button(button_frame, text="Gruppen löschen", command=self.gruppen_loeschen)
        self.btn_loeschen = ttk.Button(button_frame, text="Klassen löschen", command=self.klassen_loeschen)

        self.btn_del_users = ttk.Button(button_frame, text="Benutzer ohne Mobilgerät löschen",
                                        command=self.delete_users_wo_md)

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

    def show_about(self):
        messagebox.showinfo("Über Classload", "Classload\nVersion 1.0\n(c) 2025")

    def show_help(self):
        help_text = self.load_markdown_file("HILFE.md")
        self.show_markdown_window("Hilfe", help_text)

    def load_markdown_file(self, filename):
        if not os.path.exists(filename):
            return f"Datei '{filename}' nicht gefunden."
        with open(filename, "r", encoding="utf-8") as f:
            return markdown.markdown(f.read())

    def show_markdown_window(self, title, html_content):
        window = ttk.Toplevel(self.root)
        window.title(title)
        window.geometry("600x400")

        html_label = HTMLLabel(window, html=html_content)
        html_label.pack(fill="both", expand=True, padx=10, pady=10)

    def konfigurieren(self):
        def speichern():
            set_config_value("TEACHER_GROUP_NAME", entry_teachergroup.get())
            set_config_value("SITE_ID", entry_site_id.get())
            set_config_value("OUTPUT_FILE_CLASSES", entry_output_classes.get())
            set_config_value("OUTPUT_FILE_STUDENTS", entry_output_sus.get())
            set_config_value("POSTFIX", entry_postfix.get())
            set_config_value("TEACHER_POSTFIX", entry_lehrkraefte_postfix.get())
            # Messagebox.ok(title="Eingaben gespeichert", "Eingaben gespeichert", alert=False)
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
        ttk.Label(popup, text="Statische Benutzergruppe aller Lehrkräfte in JAMF:").grid(row=0, column=0, sticky='e',
                                                                                         padx=5, pady=2)
        entry_teachergroup = ttk.Entry(popup)
        tg = config.get_config_value("TEACHER_GROUP_NAME")
        entry_teachergroup.insert(0, tg)
        entry_teachergroup.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(popup, text="SITE-ID:").grid(row=1, column=0, sticky='e', padx=5, pady=2)
        entry_site_id = ttk.Entry(popup)
        sid = get_config_value("SITE_ID")
        entry_site_id.insert(0, sid)
        entry_site_id.grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(popup, text="Pfad zur Ausgabe aktualisierter Schüler:").grid(row=2, column=0, sticky='e', padx=5,
                                                                               pady=2)
        entry_output_sus = ttk.Entry(popup)
        ofs = get_config_value("OUTPUT_FILE_STUDENTS")
        entry_output_sus.insert(0, ofs)
        entry_output_sus.grid(row=2, column=1, padx=5, pady=2)

        ttk.Label(popup, text="Pfad zur Ausgabe der Classroom-Klassen-Daten:").grid(row=3, column=0, sticky='e', padx=5,
                                                                                    pady=2)
        entry_output_classes = ttk.Entry(popup)
        ofc = get_config_value("OUTPUT_FILE_CLASSES")
        entry_output_classes.insert(0, ofc)
        entry_output_classes.grid(row=3, column=1, padx=5, pady=2)

        ttk.Label(popup, text="Mögliches Postfix für JAMF-Schüler-Benutzer ggf. mit Leerzeichen:").grid(row=4, column=0,
                                                                                                        sticky='e',
                                                                                                        padx=5, pady=2)
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
        praefix = ""
        teachergroup = ""

        def on_submit():
            praefix = prefix_entry.get()
            teachergroup = teachergroup_entry.get()
            set_config_value("TEACHER_GROUP_NAME", teachergroup)
            if not praefix or not teachergroup:
                # Messagebox.ok(title="Fehler", "Die Werte dürfen nicht leer sein!", alert=True)
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
            teachergroup = get_config_value("TEACHER_GROUP_NAME")
            threading.Thread(target=self.klassenupload_ausfuehren, args=(dateipfad, praefix, teachergroup),
                             daemon=True).start()

    def schueler_ipads_zuordnen(self):
        """Upload mit Zuordnung der Schülernamen zu Seriennummern gemäß csv."""
        # Messagebox.ok(title="Datei auswählen","Bitte csv mit 3 Spalten auswählen: Vorname, Nachname, Seriennummer", alert=False)
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
            threading.Thread(target=schueler_ipads_aktualisieren, args=(self.JAMF_URL, self.TOKEN, dateipfad),
                             daemon=True).start()

    def lehrer_ipads_zuordnen(self):
        """Upload mit Zuordnung der Schülernamen zu Seriennummern gemäß csv."""
        # Messagebox.ok(title="Datei auswählen", "Bitte csv mit 4 Spalten auswählen: Vorname, Nachname, eindeutiges Kürzel, Seriennummer", alert=False)
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
            threading.Thread(target=lehrer_ipads_aktualisieren, args=(self.JAMF_URL, self.TOKEN, dateipfad),
                             daemon=True).start()

    def it_nummern_hochladen(self):
        """Upload mit Zuordnung der Schülernamen zu Seriennummern gemäß csv."""
        # Messagebox.ok(title="Datei auswählen", "Bitte csv mit 2 Spalten auswählen: Asset Tag (IT-Nummer, alert=False), Seriennummer")
        Messagebox.ok(
            title="Datei auswählen",
            message="Bitte csv mit 2 Spalten auswählen: Asset Tag (IT-Nummer); Seriennummer",
        )
        # antwort = askokcancel("Datei auswählen","CSV auswählen")
        # Datei auswählen

        dateipfad = filedialog.askopenfilename(title="CSV auswählen",
                                               filetypes=(("CSV-Dateien", "*.csv"), ("Alle Dateien", "*.*")))
        if not dateipfad:
            LOGGER.error("❌ Kein Dateipfad ausgewählt!")
            return
        else:
            threading.Thread(target=it_nummern_hochladen, args=(self.JAMF_URL, self.TOKEN, dateipfad),
                             daemon=True).start()

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
        praefix = ""
        teachergroup = ""

        def on_submit():
            praefix = prefix_entry.get()
            teachergroup = teachergroup_entry.get()
            set_config_value("TEACHER_GROUP_NAME", teachergroup)
            if not praefix or not teachergroup:
                # Messagebox.ok(title="Fehler", "Die Werte dürfen nicht leer sein!", alert=True)
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
            teachergroup = get_config_value("TEACHER_GROUP_NAME")
            threading.Thread(target=self.gruppen_upload_ausfuehren, args=(dateipfad, praefix, teachergroup),
                             daemon=True).start()

    def klassen_loeschen(self):
        # Präfix eingeben
        popup = ttk.Toplevel(self.root)
        popup.title("Klassen-Präfix")
        popup.geometry("600x300")
        ttk.Label(popup, text="Bitte das Klassen-Präfix, der Klassen eingeben, die gelöscht werden sollen: ").pack(
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
            threading.Thread(target=self.klassen_loeschen_ausfuehren, args=(del_praefix,), daemon=True).start()

        ttk.Button(popup, text="Bestätigen", command=on_submit).pack(pady=10)

    def single_group_upload(self):
        popup = ttk.Toplevel(self.root)
        popup.title("Klassen-Namen eingeben")
        popup.geometry("800x200")
        ttk.Label(popup,
                  text="Bitte den Namen, der Klassen eingeben, zu der eine statische Benutzergruppe angelegt werden soll: ").pack(
            pady=5)
        class_entry = ttk.Entry(popup)
        class_entry.pack(pady=5)

        def on_submit():
            classname = class_entry.get()
            print(classname);
            if not classname:
                # Messagebox.ok(title="Fehler", "Bitte alles ausfüllen!", alert=True)
                Messagebox.ok(
                    title="Alles ausgefüllt?",
                    message="Bitte alles ausfüllen.",
                    alert=True
                )
                return
            popup.destroy()
            threading.Thread(target=create_single_user_group, args=(self.JAMF_URL, self.TOKEN, classname),
                             daemon=True).start()

        ttk.Button(popup, text="Bestätigen", command=on_submit).pack(pady=10)

    def gruppen_loeschen(self):
        # Präfix eingeben
        popup = ttk.Toplevel(self.root)
        popup.title("Gruppen-Präfix")
        popup.geometry("600x300")
        ttk.Label(popup,
                  text="Bitte das Gruppen-Präfix, der Benutzergruppen eingeben, die gelöscht werden sollen: ").pack(
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
        ok_del = askokcancel("Bestätigen", "Alle Benutzer ohne Mobilgerät werden gelöscht (Lehrkräfte ausgenommen).")
        if ok_del:
            threading.Thread(target=delete_users_without_devices, args=(self.JAMF_URL, self.TOKEN), daemon=True).start()
        else:
            return

    def klassen_loeschen_ausfuehren(self, del_praefix):

        antwort = messagebox.askokcancel("Klassen löschen nach Präfix",
                                         f"Alle Klassen in JAMF mit dem Präfix {del_praefix} werden gelöscht.")

        if antwort:
            loesche_klassen_mit_prefix(self.JAMF_URL, self.TOKEN, del_praefix)
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
                    target=lambda: loesche_klassen_mit_prefix(self.JAMF_URL, self.TOKEN, del_praefix),
                    daemon=True
                ).start()
            else:
                print("Abgebrochen")

        # Dialog sicher im Hauptthread ausführen
        self.root.after(0, frage)
    """

    def gruppen_loeschen_ausfuehren(self, del_praefix):

        antwort = messagebox.askokcancel("Gruppen löschen nach Präfix",
                                         f"Alle Benutzergruppen in JAMF mit dem Präfix {del_praefix} werden gelöscht.")

        if antwort:
            loesche_usergroups_mit_prefix(self.JAMF_URL, self.TOKEN, del_praefix)
        else:
            return

    def klassenupload_ausfuehren(self, dateipfad, praefix, teachergroupname):

        # print(teachergroupname)
        SITE_ID = get_config_value("SITE_ID")
        OUTPUT_FILE_CLASSES = get_config_value("OUTPUT_FILE_CLASSES")
        OUTPUT_FILE_STUDENTS = get_config_value("OUTPUT_FILE_STUDENTS")
        POSTFIX = get_config_value("POSTFIX")
        big_merge(self.JAMF_URL, self.TOKEN, dateipfad, SITE_ID, teachergroupname, praefix, OUTPUT_FILE_STUDENTS,
                  OUTPUT_FILE_CLASSES, POSTFIX)

    def gruppen_upload_ausfuehren(self, dateipfad, praefix, teachergroupname):

        # print(teachergroupname)
        SITE_ID = get_config_value("SITE_ID")
        OUTPUT_FILE_CLASSES = get_config_value("OUTPUT_FILE_CLASSES")
        OUTPUT_FILE_STUDENTS = get_config_value("OUTPUT_FILE_STUDENTS")
        POSTFIX = get_config_value("POSTFIX")
        create_user_groups(self.JAMF_URL, self.TOKEN, dateipfad, SITE_ID, teachergroupname, praefix,
                           OUTPUT_FILE_STUDENTS,
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
