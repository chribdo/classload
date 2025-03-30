# benutzer_von_csv_liste_loeschen.py
import requests, json, logging
from logging_config import LOGGER

# 🔹 die csv-Datei (z.B. deleteUsers.csv) muss die Namen der Benutzer enthalten, die gelöscht werden sollen.
#  so eine Liste kann man direkt aus Jamf exportieren um z.B. Benutzer ohne Mobile Devices zu löschen.

def getUsers(JAMF_URL, token):
    # holt alle Benutzer von JAMF
    url = f"{JAMF_URL}/JSSResource/users"
    headers = { "Authorization": f"Bearer {token}",
                "Content-Type": "application/xml", 
                "Accept": "application/json"
               }
    response = requests.get(url, headers=headers)
    
    if response.status_code in (200,201):
        #group_id = response.text.split("<id>")[1].split("</id>")[0]  # ID aus XML extrahieren
        try:
            json_data = response.json()  # JSON-Inhalt extrahieren
            LOGGER.info("Benutzer erfolgreich abgerufen.")
        except json.JSONDecodeError:
            LOGGER.error("Fehler: Die Antwort ist kein gültiges JSON.")
            json_data = None
    else:
        LOGGER.error(f"Fehler: HTTP-Statuscode {response.status_code}")
        json_data = None
    return json_data

# 🔹 CSV Datei in Jason umwandeln
def csv_to_json(csv_file):
    data = {}
    
    # Öffne die CSV-Datei und lese den Inhalt
    with open(csv_file, mode='r', encoding='utf-8') as file:
        csv_reader = file.readlines()  # Jede Zeile einzeln lesen
        
        for row in csv_reader:
            name = row.strip()  # Entfernt Leerzeichen und Zeilenumbrüche
            if name:
                data[name] = {"name": name}  # Speichert nur den Namen
    return data

def merge_json(JAMF_URL, token, csv_file, json_data):
    
    # Lade die CSV-Daten
    csv_data = csv_to_json(csv_file)

    # Aktualisiere CSV-Daten mit den IDs aus jsondata
    filtered_users = []
    id_list = []
    for user in json_data.get("users", []):
        name = user.get("name")
        user_id = user.get("id")
        if name in csv_data:
            csv_data[name]["id"] = user_id
            filtered_users.append(csv_data[name])
            id_list.append(user_id)  # Füge die ID zur Liste hinzu
    LOGGER.info("Liste zu löschender Benutzer erstellt.")
    LOGGER.info(filtered_users)
    LOGGER.info(id_list)
    for i in range(len(id_list)):
        url = f"{JAMF_URL}/JSSResource/users/id/{id_list[i]}"
        headers = {
            "Content-Type": "application/xml",
            "Accept": "application/xml",
            "Authorization": f"Bearer {token}"
        }
        response = requests.delete(url, headers=headers)
        if response.status_code in (200,201):
            LOGGER.info(id_list[i])
            LOGGER.info("Benutzer erfolgreich gelöscht!")
        else:
            LOGGER.error(f"Fehler beim Ändern: {response.text}")


def loesche_benutzer_von_csv(JAMF_URL, TOKEN, INPUT_DELETE_FILENAME):
    token = TOKEN
    users = getUsers(JAMF_URL,token)
    merge_json(JAMF_URL, token, INPUT_DELETE_FILENAME, users)
