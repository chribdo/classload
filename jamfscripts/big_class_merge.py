import requests, json, csv
import xml.etree.ElementTree as ET
from jamfscripts.logging_config import LOGGER
import tkinter


def load_json(file_path):
    """öffnet eine JSON-Datei und gibt sie zurück"""
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

def save_json(data, file_path):
    """speichert eine JSON-Datei am gewünschten Ort"""
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def get_site_id(JAMF_URL, token):
    """liefert die SITE-ID (der Schule)"""
    url = f"{JAMF_URL}/JSSResource/sites"
    headers = {"Authorization": f"Bearer {token}",
               "Content-Type": "application/xml",
               "Accept": "application/json"
               }
    # LOGGER.info("SITE-ID ermitteln....")
    response = requests.get(url, headers=headers)
    siteinfos = response.json()
    seiteninfo = siteinfos["sites"][0]
    id = seiteninfo["id"]
    return id

def get_site_name(JAMF_URL, token):
    """liefert den Namen der Site (der Schule)"""
    url = f"{JAMF_URL}/JSSResource/sites"
    headers = {"Authorization": f"Bearer {token}",
               "Content-Type": "application/xml",
               "Accept": "application/json"
               }
    # LOGGER.info("SITE-Name ermitteln...")
    response = requests.get(url, headers=headers)
    siteinfos = response.json()
    seiteninfo = siteinfos["sites"][0]
    name = seiteninfo["name"]
    return name

def get_users(JAMF_URL, token):
    """gibt alle Benutzer der SITE zurück"""
    url = f"{JAMF_URL}/JSSResource/users"
    headers = {"Authorization": f"Bearer {token}",
               "Content-Type": "application/xml",
               "Accept": "application/json"
               }
    LOGGER.info("Importiere Benutzer von JAMF. Das dauert ein paar Minuten ...")
    response = requests.get(url, headers=headers)

    if response.status_code in (200, 201):
        # group_id = response.text.split("<id>")[1].split("</id>")[0]  # ID aus XML extrahieren
        try:
            json_data = response.json()  # JSON-Inhalt extrahieren
        except json.JSONDecodeError:
            LOGGER.info("Fehler: Die Antwort ist kein gültiges JSON")
            json_data = None
    else:
        LOGGER.error(f"Fehler: HTTP-Statuscode {response.status_code}")
        json_data = None
    LOGGER.info("Benutzer von JAMF wurden importiert.")
    return json_data

def csv_to_json(csv_file):
    """wandelt eine CSV mit iServ-Schüler-Daten in ein JSON um."""
    data = {}

    # Öffne die CSV-Datei und lese den Inhalt
    with open(csv_file, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file,
                                    delimiter=';')  # Liest jede Zeile als Dictionary mit Semikolon als Trennzeichen

        for row in csv_reader:
            vorname = row.get("Vorname", "")
            nachname = row.get("Nachname", "")
            name = vorname + " " + nachname
            klasse = row.get("Klasse/Information", "")
            kurse = row.get("Gruppen", "").split(',') if row.get("Gruppen") else []

            data[name] = {  # Schlüssel ist der Name, da ID nur in users.json existiert
                "name": name,
                "klasse": klasse,
                "kurse": kurse
            }
    LOGGER.info("CSV mit iServ-Schueler_innen wurde importiert.")
    return data

def merge_students(csv_data, json_data, output_file, postfix):
    """iServ- und JAMF-Benutzerdaten werden zusammengeführt."""
    merged_data = []
    for user in json_data.get("users", []):
        name = user.get("name")
        name_w_postfix = name
        hat_postfix = False
        if name.find(postfix) > -1:
            name = name.replace(postfix, "")
            hat_postfix = True
        if name in csv_data:
            user.update(csv_data[name])
            if hat_postfix:
                user["name"] = name_w_postfix
        merged_data.append(user)

    #  Speichere das zusammengeführte JSON
    with open(output_file, mode='w', encoding='utf-8') as file:
        json.dump({"users": merged_data}, file, indent=4, ensure_ascii=False)
        LOGGER.info("Datei geschrieben")
    LOGGER.info("JAMF- und iServ Schuelerdaten wurden zusammengeführt.")
    return {"users": merged_data}

def extract_courses(data):
    """ Kursdaten aus zusammengeführten Schülerdaten (Parameter data) erzeugen"""
    courses = {}
    student_classes = {}
    for user in data["users"]:
        user_id = user["id"]
        user_class = user.get("klasse", "").replace("Klasse", "").strip()  # Entferne "Klasse"
        student_classes[user_id] = user_class
        if "kurse" in user:  # Überprüfung, ob 'kurse' existiert
            for course in user["kurse"]:
                if course not in courses:
                    courses[course] = []
                courses[course].append({"id": user_id})
    LOGGER.info("Die Kursstruktur wurde aus den Schülerdaten extrahiert.")
    return courses, student_classes

def fetch_teachers(JAMF_URL, token, TEACHER_GROUP_NAME):
    """
    Hilfsfunktion von get_teachers.
    Holt alle Lehrkräfte_Benutzer (der Site) von JAMF und gibt sie als JSON zurück.
    """
    url = f"{JAMF_URL}/JSSResource/usergroups/name/{TEACHER_GROUP_NAME}"
    headers = {"Authorization": f"Bearer {token}",
               "Content-Type": "application/xml",
               "Accept": "application/json"
               }

    response = requests.get(url, headers=headers)

    if response.status_code in (200, 201):
        try:
            json_data = response.json()  # JSON-Inhalt extrahieren
        except json.JSONDecodeError:
            LOGGER.critical("Fehler: Die Antwort ist kein gültiges JSON")
            json_data = None
    else:
        LOGGER.critical(f"Fehler: HTTP-Statuscode {response.status_code}")
        json_data = None
    LOGGER.info("Die Lehrkräfte-Daten wurden von JAMF importiert.")
    return json_data

def get_teachers(JAMF_URL, token, TEACHER_GROUP_NAME):
    """holt Lehrkraft-Informationen von JAMF und gibt sie aufbereitet zurück."""
    teacher_data = fetch_teachers(JAMF_URL, token, TEACHER_GROUP_NAME)
    teachers = {}
    for teacher in teacher_data["user_group"]["users"]:
        phone_number = teacher.get("phone_number", "")
        if phone_number:
            teachers[phone_number] = teacher["id"]
    LOGGER.info("Die Lehrkräftedaten wurden aufbereitet")
    return teachers

def switch_fach(value):
    """verschönert die Informationen zum Fach. Aus 'D' wird z.B. 'Deutsch'"""
    match value:
        case "D":
            return "Deutsch"
        case "M":
            return "Mathematik"
        case "IF":
            return "Informatik"
        case "MU":
            return "Musik"
        case "PH":
            return "Physik"
        case "CH":
            return "Chemie"
        case "KU":
            return "Kunst"
        case "SP":
            return "Sport"
        case "EK":
            return "Erdkunde"
        case "E147":
            return "Englisch"
        case "FB":
            return "Förderband"
        case "GE":
            return "Geschichte"
        case "BI":
            return "Biologie"
        case "PK":
            return "Politik"
        case "F149":
            return "Französisch"
        case "L149":
            return "Latein"
        case "Schw":
            return "Schwimmen"
        case "KR":
            return "Kath. Religion"
        case "ER":
            return "Ev. Religion"
        case "PP":
            return "Praktische Philosophie"
        case "PL":
            return "Philosophie"
        case _:
            return value

def get_fach(bez):
    """Extrahiert das Fachkürzel aus einem komplexen Klassennamen wie '25d_U KU - Haak - 152C'."""
    try:
        nach_unterstrich = bez.split("_", 1)[1].strip()  # z. B. 'U KU - Haak - 152C'
        teile = nach_unterstrich.split()
        if len(teile) >= 2:
            fach_kurz = teile[1].split("-")[0].strip()
            fach_lang = switch_fach(fach_kurz)
            print(f"[DEBUG] bez: {bez} → fach_kurz: {fach_kurz} → fach_lang: {fach_lang}")
            return fach_lang
        else:
            print(f"[DEBUG] bez: {bez} → Zu wenig Teile nach Unterstrich")
            return bez
    except (IndexError, ValueError) as e:
        print(f"[DEBUG] Fehler bei get_fach({bez}): {e}")
        return bez

"""
def get_fach(bez):
    
    teile = bez.split()
    if (teile[0] == "U"):
        wort = teile[1]
        teile_b = wort.split("-")
        fach = teile_b[0]
        fach = switch_fach(fach)
        return fach
    else:
        return bez
"""

def create_class_structure(course_data, site_id, prefix, teacher_data, student_classes, output_file):
    """Die Klassenstruktur wird erstellt mit Lehrkräften und Schülern. Das Ganze wird als json abgespeichert."""
    classes = []
    postfix = 0
    seen_class_names = set()
    for course_name, students in course_data.items():

        full_class_name: str = f"{prefix}{course_name}".replace("Unterricht", "U")  # Ersetze "Unterricht" durch "U"
        teilwort = ' - '
        k_name_wo_postfix = ''
        count = full_class_name.count(teilwort)
        if count >= 2:
            k_name_wo_postfix = ''
            first_hyphen = full_class_name.find(teilwort)
            second_hyphen = full_class_name.find(teilwort, first_hyphen + len(teilwort))
            cut_index = second_hyphen + 7
            if (cut_index < len(full_class_name)):
                if (full_class_name[cut_index] != ' '):
                    cut_index = cut_index - 7
                full_class_name = full_class_name[:cut_index]
                k_name_wo_postfix = full_class_name
                if full_class_name in seen_class_names:
                    full_class_name += str(postfix)
                    postfix += 1
            seen_class_names.add(k_name_wo_postfix)
        teacher_ids = [teacher_id for phone, teacher_id in teacher_data.items() if phone in full_class_name]

        # Ermitteln der einzigartigen Klassen der Schüler für die Beschreibung
        unique_classes = sorted(
            set(student_classes[student["id"]] for student in students if student["id"] in student_classes))
        description = ", ".join(unique_classes)
        description = get_fach(full_class_name) + " " + description

        class_entry = {
            "class": {
                "name": full_class_name,
                "site": {"id": site_id},
                "student_ids": [{"id": student["id"]} for student in students],
                "teacher_ids": teacher_ids,  # Lehrer IDs anhand des Klassennamens
                "description": description
            }
        }
        classes.append(class_entry)

    save_json(classes, output_file)
    LOGGER.info("Die Daten für die JAMF-Klassen wurden erstellt.")
    LOGGER.info(f"Datei {output_file} wurde erfolgreich erstellt.")

def create_xml_from_class(class_data):
    """erstellt ein XML-Objekt aus den übergebenen Klassendaten"""
    class_element = ET.Element("class")

    name_element = ET.SubElement(class_element, "name")
    name_element.text = class_data["class"]["name"]

    description_element = ET.SubElement(class_element, "description")
    description_element.text = class_data["class"]["description"]

    site_element = ET.SubElement(class_element, "site")
    site_id_element = ET.SubElement(site_element, "id")
    site_id_element.text = str(class_data["class"]["site"]["id"])

    students_element = ET.SubElement(class_element, "student_ids")
    for student in class_data["class"]["student_ids"]:
        student_id_element = ET.SubElement(students_element, "id")
        student_id_element.text = str(student["id"])

    teachers_element = ET.SubElement(class_element, "teacher_ids")
    for teacher_id in class_data["class"]["teacher_ids"]:
        teacher_id_element = ET.SubElement(teachers_element, "id")
        teacher_id_element.text = str(teacher_id)
    return ET.tostring(class_element, encoding="utf-8").decode("utf-8")

def big_merge(JAMF_URL, TOKEN, INPUT_FILENAME, SITE_ID, TEACHER_GROUP_NAME, CLASS_PREFIX, OUTPUT_FILE_STUDENTS,
              OUTPUT_FILE_CLASSES, postfix, parent=None):
    """
    Diese Funktion ist das Herzstück von Classload und führt alles zusammen.
    Die mithilfe der iServ-Schüler-Daten-csv und mit JAMF-API-Zugriffen vorbereiteten Klassen
    werden zu JAMF hochgeladen.
    """
    from jamfscripts.authentifizierung import refresh_token
    csv_data = csv_to_json(INPUT_FILENAME)
    token = TOKEN
    # get_site_id(JAMF_URL, token)
    users = get_users(JAMF_URL, token)
    schueler = merge_students(csv_data, users, OUTPUT_FILE_STUDENTS, postfix)
    LOGGER.info("IServ- und Jamf-Schülerdaten abgeglichen.")
    courses, student_classes = extract_courses(schueler)
    teachers = get_teachers(JAMF_URL, token, TEACHER_GROUP_NAME)
    LOGGER.info("Lehrer geholt.")
    LOGGER.info("Class-Prefix: "+ CLASS_PREFIX)
    create_class_structure(courses, SITE_ID, CLASS_PREFIX, teachers, student_classes, OUTPUT_FILE_CLASSES)
    class_data = load_json(OUTPUT_FILE_CLASSES)
    #LOGGER.info("Jetzt kommt die askokcancel-Abfrage")
    ok=True
    if parent is not None:
        ok = tkinter.messagebox.askokcancel(
        "Bestätigen",
        "Der Klassenupload kann beginnen.",
        parent=parent)
    # ok = tkinter.messagebox.askokcancel("Bestätigen", "Der Klassenupload kann beginnen.")
    if not ok:
        LOGGER.info("Cancel gewählt")
        return
    else:
        LOGGER.info("OK gewählt")
        url = f"{JAMF_URL}/JSSResource/classes/id/0"
        headers = {
            "Content-Type": "application/xml",
            "Accept": "application/xml",
            "Authorization": f"Bearer {token}"
        }
        i=0
        for class_entry in class_data:
            if (i%40==0):
                TOKEN= refresh_token(JAMF_URL, TOKEN)
            i=i+1
            xml_string = create_xml_from_class(class_entry)
            LOGGER.info(class_entry["class"]["name"])

            # EINKOMMENTIEREN FÜR UPLOAD
            
            response = requests.post(url, headers=headers, data=xml_string)
            if response.status_code in (200,201):
              LOGGER.info("Klasse erfolgreich erstellt!")
            else:
              LOGGER.error(f"Fehler beim Erstellen der Klasse: {response.text}")

        LOGGER.info("Upload abgeschlossen.")
