import json
import xml.etree.ElementTree as ET
from jamfscripts.big_class_merge import *
from jamfscripts.authentifizierung import refresh_token


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
def create_group_xml_from_class(class_data):
    group_element = ET.Element("user_group")

    name_element = ET.SubElement(group_element, "name")
    name_element.text = class_data["class"]["name"]

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

def create_user_groups(JAMF_URL, TOKEN, INPUT_FILENAME, SITE_ID, TEACHER_GROUP_NAME, CLASS_PREFIX, OUTPUT_FILE_STUDENTS, OUTPUT_FILE_CLASSES, postfix):
        csv_data = csv_to_json(INPUT_FILENAME)
        token = TOKEN
        # get_site_id(JAMF_URL, token)
        LOGGER.info("Der Vorgang kann sehr lange dauern.")
        users = get_users(JAMF_URL, token)
        schueler = merge_students(csv_data, users, OUTPUT_FILE_STUDENTS, postfix)
        courses, student_classes = extract_courses(schueler)
        teachers = get_teachers(JAMF_URL, token, TEACHER_GROUP_NAME)
        create_class_structure(courses, SITE_ID, CLASS_PREFIX, teachers, student_classes, OUTPUT_FILE_CLASSES)
        class_data = load_json(OUTPUT_FILE_CLASSES)


        for class_entry in class_data:
            token = refresh_token(JAMF_URL, token)
            url = f"{JAMF_URL}/JSSResource/usergroups/id/0"
            headers = {
                "Content-Type": "application/xml",
                "Accept": "application/xml",
                "Authorization": f"Bearer {token}"
            }
            xml_string = create_group_xml_from_class(class_entry)
            # print(create_group_xml_from_class(class_entry))
            LOGGER.info(class_entry["class"]["name"])

            # EINKOMMENTIEREN FÜR UPLOAD

            response = requests.post(url, headers=headers, data=xml_string)
            if response.status_code in (200, 201):
                LOGGER.info("Gruppe erfolgreich erstellt!")
            else:
                LOGGER.error(f"Fehler beim Erstellen der Gruppe: {response.text}")

        LOGGER.info("Upload abgeschlossen.")



