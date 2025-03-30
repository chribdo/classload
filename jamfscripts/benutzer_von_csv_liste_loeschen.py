# benutzer_von_csv_liste_loeschen.py
import requests, json, logging
from requests import Response

from jamfscripts.big_class_merge import fetch_teachers
from jamfscripts import refresh_token
from jamfscripts.logging_config import LOGGER
from jamfscripts.config import get_config_value

# 🔹 die csv-Datei (z.B. deleteUsers.csv) muss die Namen der Benutzer enthalten, die gelöscht werden sollen.
#  so eine Liste kann man direkt aus Jamf exportieren um z.B. Benutzer ohne Mobile Devices zu löschen.

def get_users(JAMF_URL, token):
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
            #print(json_data)
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

def delete_csv_json(JAMF_URL, token, csv_file, json_data):
    
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

def get_mobile_devices(JAMF_URL, token):
    # holt alle Mobilgeräte von JAMF
    url = f"{JAMF_URL}/JSSResource/mobiledevices"
    headers = {"Authorization": f"Bearer {token}",
               "Content-Type": "application/xml",
               "Accept": "application/json"
               }
    response = requests.get(url, headers=headers)

    if response.status_code in (200, 201):
        # group_id = response.text.split("<id>")[1].split("</id>")[0]  # ID aus XML extrahieren
        try:
            json_data = response.json()  # JSON-Inhalt extrahieren
            #print(json_data)
            LOGGER.info("Mobilgeräte erfolgreich abgerufen.")
        except json.JSONDecodeError:
            LOGGER.error("Fehler: Die Antwort ist kein gültiges JSON.")
            json_data = None
    else:
        LOGGER.error(f"Fehler: HTTP-Statuscode {response.status_code}")
        json_data = None
    return json_data

def get_username_set(JAMF_URL,token):
    data=get_mobile_devices(JAMF_URL, token)
    usernames = {device['username'] for device in data['mobile_devices'] if 'username' in device}
    return usernames

def delete_users_without_devices(JAMF_URL, token):
   usernames=get_username_set(JAMF_URL, token)
   users=get_users(JAMF_URL,token)
   tgn = get_config_value("TEACHER_GROUP_NAME")
   teachers = fetch_teachers(JAMF_URL,token,tgn)
   #print(teachers)
   teacher_names = {user['username'] for user in teachers['user_group']['users'] if 'username' in user}
   filtered_users = []
   id_list = []
   for user in users.get("users", []):
       name = user.get("name")
       user_id = user.get("id")
       if name not in usernames and name not in teacher_names:
           filtered_users.append(user["name"])
           id_list.append(user_id)  # Füge die ID zur Liste hinzu

   LOGGER.info("Diese Schülerbenutzer werden gelöscht... ")
   LOGGER.info(filtered_users)
   count=0
   for i in range(len(id_list)):
       if count==10:
           count =0
           token=refresh_token(JAMF_URL,token)
       url = f"{JAMF_URL}/JSSResource/users/id/{id_list[i]}"
       headers = {
            "Content-Type": "application/xml",
            "Accept": "application/xml",
            "Authorization": f"Bearer {token}"
        }
       response: Response = requests.delete(url, headers=headers)
       if response.status_code in (200,201):
            count=count+1
            LOGGER.info(id_list[i])
            LOGGER.info("Benutzer erfolgreich gelöscht!")
       else:
            LOGGER.error(f"Fehler beim Löschen: {response.text}")


def loesche_benutzer_von_csv(JAMF_URL, TOKEN, INPUT_DELETE_FILENAME):
    token = TOKEN
    users = get_users(JAMF_URL, token)
    delete_csv_json(JAMF_URL, token, INPUT_DELETE_FILENAME, users)
