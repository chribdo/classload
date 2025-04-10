import json
import xml.etree.ElementTree as ET

from jamfscripts import get_config_value
from jamfscripts.big_class_merge import *
from jamfscripts.authentifizierung import refresh_token


def get_class(jamf_url, token, classname):
    """Holt ein Bearer-Token von der Jamf Pro API."""
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
        print(response.status_code)
        LOGGER.error("Class Daten nicht erhalten")
        return ""
        #raise Exception(f"Fehler beim Abrufen des T


def group_merge(JAMF_URL, TOKEN, INPUT_FILENAME, OUTPUT_FILE_STUDENTS, CLASS_PREFIX,  postfix):

    csv_data = csv_to_json(INPUT_FILENAME)
    token = TOKEN
    #get_site_id(JAMF_URL, token)
    users=get_users(JAMF_URL,token)
    schueler=merge_students(csv_data, users, OUTPUT_FILE_STUDENTS, postfix)
    courses, student_classes = extract_courses(schueler)
    return courses,student_classes

def create_group_structure(course_data, prefix, output_file):
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

# 🔹 XML-Objekt aus Klassendaten erstellen
def create_group_xml_from_class(class_data, prefix):
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
    group_element = ET.Element("user_group")
    # name_element = ET.SubElement(group_element, "name")
    # name_element.text = group_name
    useradd_element = ET.SubElement(group_element, "user_additions")
    user_element = ET.SubElement(useradd_element, "user")
    user_name_element = ET.SubElement(user_element, "username")
    user_name_element.text = user_name
    return ET.tostring(group_element, encoding="utf-8").decode("utf-8")

def update_teacher_group(jamf_url, token, teacher_group_name, teacher_name):
    xml_string=create_user_addition_xml(teacher_name)
    url = f"{jamf_url}/JSSResource/usergroups/name/{teacher_group_name}"
    headers = {"Content-Type": "application/xml",
               "Accept": "application/xml",
               "Authorization": f"Bearer {token}"
               }
    # print(xml_string)
    LOGGER.info("Benutzer wird hinzugefügt. Das kann etwas dauern..")
    response = requests.put(url, headers=headers, data=xml_string)
    if response.status_code in (200, 201):
        LOGGER.info("Lehrkraft erfolgreich der Lehrergruppe hinzugefügt!")
    else:
        LOGGER.info(response.status_code)
        LOGGER.error(f"Fehler beim Hinzufügen zur Gruppe: {response.text}")

def create_single_user_group(jamf_url, token,  my_classname):
    myclass = get_class(jamf_url, token, my_classname)
    student_ids = myclass["class"]["student_ids"]
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


        for class_entry in class_data:
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



