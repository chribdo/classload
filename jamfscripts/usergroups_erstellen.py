from jamfscripts import get_config_value
from jamfscripts.big_class_merge import *
from jamfscripts.authentifizierung import refresh_token

import requests, csv
"""
import unicodedata
def sanitize_classname(name: str) -> str:
    # Trim & Unicode normalisieren (z. B. bei aus der UI kopierten Namen)
    s = name.strip()
    s = s.replace("\u00A0", " ")      # NBSP -> normaler Space
    s = s.replace("\u200B", "")       # Zero-width space entfernen
    s = unicodedata.normalize("NFC", s)
    return s
"""
def get_class(jamf_url, token, classname):
    """Holt eine Klasse mit einem bestimmten Namen von JAMF und gibt sie als json zurück."""
    url = f"{jamf_url}/JSSResource/classes/name/{classname}"
    headers = {"Authorization": f"Bearer {token}",
               "Content-Type": "application/xml",
               "Accept": "application/json"
               }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:

        LOGGER.info("Class Daten erhalten")
        return response.json()
    else:
        LOGGER.error("Class Daten nicht erhalten")
        return ""
        #raise Exception(f"Fehler beim Abrufen des T



def group_merge(JAMF_URL, TOKEN, INPUT_FILENAME, OUTPUT_FILE_STUDENTS, CLASS_PREFIX,  postfix):
    """Die Daten von JAMF und iServ werden zusammengeführt"""
    csv_data = csv_to_json(INPUT_FILENAME)
    token = TOKEN
    #get_site_id(JAMF_URL, token)
    users=get_users(JAMF_URL,token)
    schueler=merge_students(csv_data, users, OUTPUT_FILE_STUDENTS, postfix)
    courses, student_classes = extract_courses(schueler)
    return courses,student_classes

def create_group_structure(course_data, prefix, output_file):
    """Die Struktur der Benutzergruppe wird als json abgespeichert"""
    groups = []
    postfix=0
    for course_name, students in course_data.items():

        full_group_name: str = f"{prefix}{course_name}".replace("Unterricht", "U")  # Ersetze "Unterricht" durch "U"

        group_entry = {
            "user_group": {
                "name": full_group_name,
                "users": [{"id": student["id"]} for student in students],
            }
        }
        groups.append(group_entry)

    save_json(groups, output_file)
    LOGGER.info("Die Daten für die JAMF-Klassen wurden erstellt.")
    LOGGER.info(f"Datei {output_file} wurde erfolgreich erstellt.")

def create_group_xml_from_class(class_data, prefix):
    """Aus übergebenen Klassendaten wird ein XML String für eine korrespondierende statische Benutzergruppe erstellt."""
    group_element = ET.Element("user_group")
    name_element = ET.SubElement(group_element, "name")
    name_element.text = class_data["class"]["name"]
    LOGGER.info(name_element.text)

    is_smart_element = ET.SubElement(group_element, "is_smart")
    is_smart_element.text = "false"

    site_element = ET.SubElement(group_element, "site")
    site_id_element = ET.SubElement(site_element, "id")
    site_id_element.text = str(class_data["class"]["site"]["id"])


    users_element = ET.SubElement(group_element, "users")
    for student in class_data["class"]["student_ids"]:
        user_element = ET.SubElement(users_element, "user")
        student_id_element = ET.SubElement(user_element, "id")
        student_id_element.text = str(student["id"])
    return ET.tostring(group_element, encoding="utf-8").decode("utf-8")

def create_group_xml(name, liste):
    """
    Erstellt aus einer Liste von Benutzernamen einen XML-String
    zu einer statischen Benutzergruppe mit dem Namen des Werts des 1. Parameters.
    """
    group_element = ET.Element("user_group")

    name_element = ET.SubElement(group_element, "name")
    name_element.text = name

    is_smart_element = ET.SubElement(group_element, "is_smart")
    is_smart_element.text = "false"

    site_element = ET.SubElement(group_element, "site")
    site_id_element = ET.SubElement(site_element, "id")
    site_id_element.text = str(get_config_value("SITE_ID"))


    users_element = ET.SubElement(group_element, "users")
    for student in liste:
        user_element = ET.SubElement(users_element, "user")
        student_id_element = ET.SubElement(user_element, "id")
        student_id_element.text = str(student)
    return ET.tostring(group_element, encoding="utf-8").decode("utf-8")

def create_user_addition_xml(user_name):
    """
    Der XML-String, der hier zurückgegeben wird,
    dient an anderer Stelle dazu Informationen zum Hinzufügen eines Benutzers zu übermitteln
    """
    group_element = ET.Element("user_group")
    # name_element = ET.SubElement(group_element, "name")
    # name_element.text = group_name
    useradd_element = ET.SubElement(group_element, "user_additions")
    user_element = ET.SubElement(useradd_element, "user")
    user_name_element = ET.SubElement(user_element, "username")
    user_name_element.text = user_name
    return ET.tostring(group_element, encoding="utf-8").decode("utf-8")

def update_teacher_group(jamf_url, token, teacher_group_name, teacher_name):
    """
        Die Lehrerbenutzergruppe wird um einen Benutzer mit Namen teacher_name ergänzt.
    """
    xml_string=create_user_addition_xml(teacher_name)
    url = f"{jamf_url}/JSSResource/usergroups/name/{teacher_group_name}"
    headers = {"Content-Type": "application/xml",
               "Accept": "application/xml",
               "Authorization": f"Bearer {token}"
               }
    # print(xml_string)
    LOGGER.info("Benutzer wird der Lehrergruppe hinzugefügt...")
    response = requests.put(url, headers=headers, data=xml_string)
    if response.status_code in (200, 201):
        LOGGER.info("Lehrkraft erfolgreich der Lehrergruppe hinzugefügt!")
    else:
        LOGGER.info(response.status_code)
        LOGGER.error(f"Fehler beim Hinzufügen zur Gruppe: {response.text}")

def create_single_user_group(jamf_url, token,  my_classname):
    """
    Zu einer einzelnen Klasse (der Klassennname wird als Parameter übergeben)
    wird eine korrespondierende statische Benutzergruppe erzeugt.
    """
    myclass = get_class(jamf_url, token, my_classname)
    #print(myclass)
    if not isinstance(myclass, dict):
        LOGGER.error(f"❌ Abbruch: Klasse '{my_classname}' nicht gefunden/erhalten oder ungültiges Format: {myclass}")
        return

    try:
        student_ids = myclass["class"]["student_ids"]
    except (KeyError, TypeError) as e:
        LOGGER.error(f"❌ Abbruch: Klasse nicht gefunden/erhalten: '{my_classname}': {e}")
        return
    #student_ids = myclass["class"]["student_ids"]
    # print(student_ids)
    xml_string = create_group_xml(my_classname, student_ids)
    #print(xml_string)
    url = f"{jamf_url}/JSSResource/usergroups/id/0"
    headers = {"Content-Type": "application/xml",
               "Accept": "application/xml",
               "Authorization": f"Bearer {token}"
               }
    # print(xml_string)
    LOGGER.info("Gruppe wird erstellt. Das kann etwas dauern..")
    response = requests.post(url, headers=headers, data=xml_string)
    if response.status_code in (200, 201):
        LOGGER.info("Gruppe erfolgreich erstellt!")
    else:
        LOGGER.info(response.status_code)
        LOGGER.error(f"Fehler beim Erstellen der Gruppe: {response.text}")

def create_user_groups(JAMF_URL, TOKEN, INPUT_FILENAME, SITE_ID, TEACHER_GROUP_NAME, CLASS_PREFIX, OUTPUT_FILE_STUDENTS, OUTPUT_FILE_CLASSES, postfix, parent=None):
        """
        Zu allen Klassen werden entsprechende statische Benutzergruppen angelegt.
        Der Vorgang dauert sehr lange. Wahrscheinlich mehrere Stunden oder sogar Tage.
        """
        csv_data = csv_to_json(INPUT_FILENAME)
        token = TOKEN
        # get_site_id(JAMF_URL, token)
        LOGGER.info("Der Vorgang kann SEHR lange dauern.")
        LOGGER.info(CLASS_PREFIX)
        users = get_users(JAMF_URL, token)
        schueler = merge_students(csv_data, users, OUTPUT_FILE_STUDENTS, postfix)
        courses, student_classes = extract_courses(schueler)
        teachers = get_teachers(JAMF_URL, token, TEACHER_GROUP_NAME)
        create_class_structure(courses, SITE_ID, CLASS_PREFIX, teachers, student_classes, OUTPUT_FILE_CLASSES)
        class_data = load_json(OUTPUT_FILE_CLASSES)

        ok = True
        if parent is not None:
            ok = tkinter.messagebox.askokcancel(
                "Bestätigen",
                "Der Gruppenupload kann beginnen.",
                parent=parent)
        # ok = tkinter.messagebox.askokcancel("Bestätigen", "Der Klassenupload kann beginnen.")
        if not ok:
            LOGGER.info("Cancel gewählt")
            return
        else:
            LOGGER.info("OK gewählt")

        i=1
        for class_entry in class_data:
            LOGGER.info("Gruppe Nr. " + str(i) + " wird erstellt.")
            i = i + 1
            token = refresh_token(JAMF_URL, token)
            url = f"{JAMF_URL}/JSSResource/usergroups/id/0"
            headers = {
                "Content-Type": "application/xml",
                "Accept": "application/xml",
                "Authorization": f"Bearer {token}"
            }
            xml_string = create_group_xml_from_class(class_entry, CLASS_PREFIX)
            # print(create_group_xml_from_class(class_entry))
            #LOGGER.info(class_entry["class"]["name"])

            # EINKOMMENTIEREN FÜR UPLOAD

            response = requests.post(url, headers=headers, data=xml_string)
            if response.status_code in (200, 201):
                LOGGER.info("Gruppe erfolgreich erstellt!")
            else:
                LOGGER.error(f"Fehler beim Erstellen der Gruppe: Existiert die Gruppe mit dem Namen vielleicht bereits?")

        LOGGER.info("Upload abgeschlossen.")


def create_some_usergroups(jamf_url, token, csv_path):
    """
    Liest eine CSV-Datei ein und ruft für jede Zeile
    create_single_user_group(...) mit dem Klassennamen auf.
    """
    with open(csv_path, newline='', encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if not row:  # leere Zeilen überspringen
                continue
            my_classname = row[0].strip()  # erster Wert in der Zeile
            if my_classname:               # nur wenn nicht leer
                create_single_user_group(jamf_url, token, my_classname)


