"""
Dieses Modul erzeugt u.a. aus iServ-Benutzerdaten Klassen für die Apple-Classroom-App
Damit das funktioniert müssen
    1. die Kursstrukturen von Webuntis nach iServ per Webuntis-Connector übertragen worden sein.
    2. die Lehrkräfte müssen in JAMF in einer statischen Benutzergruppe eingetragen sein.
    3. die Lehrkräfte-Benutzer müssen in JAMF bei der Telefonnummer ihr eindeutiges, offizielles Lehrerkürzel eingetragen haben.
    4. die Schüler-Benutzer in JAMF müssen wie folgt heißen "iser-vorname iserv-nachname", z.B. "Maxi Muster"
Autorin: Christiane Borchel
Datum: 16. März 2025
"""
import getpass
from jamfscripts import get_auth_token, loesche_klassen_mit_prefix, loesche_benutzer_von_csv, big_merge, get_site_id, get_cipher


# 🔹 Jamf Pro Instanz & Zugangsdaten
#JAMF_URL = "https://dosys.jamfcloud.com"  # Deine Jamf Pro URL
#USERNAME = ""
#PASSWORD = ""

SITE_ID = 53  # ID der gewünschten Site, wenn die SITE-ID (ID der Schule bei Jamf-Instanz) nicht bekannt ist, geht auch folgendes:
#SITE_ID = get_site_id(JAMF_URL,token)

POSTFIX = " RSG" # Mögliches Postfix für Schüler-Benutzernamen. Führendes Leerzeichen nicht vergessen.
# Idee für Weiterentwicklung: Implementieren, dass als POSTFIX automatisch " " + site_name genommen wird.


default_value = "https://dosys.jamfcloud.com"
JAMF_URL = input(f"Geben den Link zur JAMF-Pro-Instanz ein oder akzeptieren Sie [{default_value}] mit Enter. ") or default_value
USERNAME = input("Benutzername: ")
PASSWORD = get_cipher().encrypt(getpass.getpass("Passwort: ").encode())
token = get_auth_token(JAMF_URL,USERNAME,PASSWORD)

# Was nett wäre: Bis jetzt werden config.json und config.py noch nicht genutzt.
# Man könnte sie für die vorgegeben Variablen aus einem Konfigurationsmenü füllen

# 1.
#
# Klassen erstellen und hochladen aus einer csv-Datei mit iserv-Benutzern
# Wichtig: Der CSV-INPUT muss folgende Spalten enthalten: Vorname;Nachname;Klasse/Information;Gruppen;
INPUT_FILENAME = "./daten/iserv_schueler.csv"  # Name der Eingabe-Dat# ei, kann einfach von iServ exportiert werden.
TEACHER_GROUP_NAME = "Lehrer RSGL" # Statische Benutzergruppe aller Lehrkräfte
OUTPUT_FILE_CLASSES = "./daten/alle_klassen.json"  # Muss nicht verändert werden. Die Klassen werden zusätzlich zum Upload lokal gespeichert.
OUTPUT_FILE_STUDENTS = "./daten/merged_schueler.json"  # Muss nicht verändert werden. Die zusammengeführten Schülerdaten werden zusätzlich zum Upload lokal gespeichert.

PREFIX = "25b" # Gewünschtes PREFIX für alle Klassennamen. Dient zur Identifikation, welche Klassen gerade aktuell sind.

# big_merge(JAMF_URL,token,INPUT_FILENAME,SITE_ID,TEACHER_GROUP_NAME, PREFIX,OUTPUT_FILE_STUDENTS, OUTPUT_FILE_CLASSES, POSTFIX)


# 2.
#
# Zum Löschen aller Klassen mit einem bestimmten Präfix
PREFIX_DEL = "25d"
# loesche_klassen_mit_prefix(JAMF_URL,token, PREFIX_DEL)



# 3.
#
# Zum Löschen einer csv mit Benutzern (Benutzernamen), z.B. Benutzern ohne Mobile Device (iPad)
INPUT_DELETE_FILENAME = "./daten/deleteUsers.csv"  # gewünschten Dateinamen für zu löschende Benutzer eingeben
# loesche_benutzer_von_csv(JAMF_URL,token, INPUT_DELETE_FILENAME)