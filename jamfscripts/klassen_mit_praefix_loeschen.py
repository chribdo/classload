# klassen_mit_praefix_loeschen.py
import requests, json, os

from jamfscripts import refresh_token
from jamfscripts.logging_config import LOGGER



def get_classes(JAMF_URL, token):
    url = f"{JAMF_URL}/JSSResource/classes"
    headers = { "Authorization": f"Bearer {token}",
                "Content-Type": "application/xml",
                "Accept": "application/json"
               }

    response = requests.get(url, headers=headers)

    if response.status_code in (200,201):
        LOGGER.info("Klassen erfolgreich abgerufen.")
        try:
            json_data = response.json()  # JSON-Inhalt extrahieren
        except json.JSONDecodeError:
            LOGGER.error("Fehler: Die Antwort ist kein gültiges JSON")
            json_data = None
    else:
        LOGGER.error(f"Fehler: HTTP-Statuscode {response.status_code}")
        json_data = None
    #print(json_data)
    return json_data

def filter_and_delete_classes(JAMF_URL, token, PREFIX, json_data):

    filtered_classes = []
    id_list = []
    for c in json_data.get("classes", []):
        name = c.get("name")
        if(name[:len(PREFIX)]==PREFIX):
          class_id = c.get("id")
          filtered_classes.append(c)
          id_list.append(class_id)  # Füge die ID zur Liste hinzu
    #print(id_list)
    count = 0
    for i in range(len(id_list)):
        if count == 10:
            count = 0
            token = refresh_token(JAMF_URL, token)

        url = f"{JAMF_URL}/JSSResource/classes/id/{id_list[i]}"
        headers = {
            "Content-Type": "application/xml",
            "Accept": "application/xml",
            "Authorization": f"Bearer {token}"
        }
        response = requests.delete(url, headers=headers)
        if response.status_code in (200,201):
            count+=1
            print(id_list[i])
            print("Klasse erfolgreich gelöscht!")
        else:
            print(f"Fehler beim Löschen: {response.text}")

def loesche_klassen_mit_prefix(JAMF_URL,TOKEN, PREFIX):
    token=TOKEN
    classes=get_classes(JAMF_URL, token)
    filter_and_delete_classes(JAMF_URL, PREFIX, classes)
    LOGGER.info("Löschen abgeschlossen")


