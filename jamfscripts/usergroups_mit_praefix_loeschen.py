import requests, json
from jamfscripts.logging_config import LOGGER
from jamfscripts.authentifizierung import refresh_token

def get_usergroups(JAMF_URL, token):
    """holt alle Usergroups (einer SITE/Schule) von JAMF und gibt sie als JSON zurück"""
    url = f"{JAMF_URL}/JSSResource/usergroups"
    headers = { "Authorization": f"Bearer {token}",
                "Content-Type": "application/xml",
                "Accept": "application/json"
               }

    response = requests.get(url, headers=headers)

    if response.status_code in (200,201):
        LOGGER.info("Usergroups erfolgreich abgerufen.")
        try:
            json_data = response.json()  # JSON-Inhalt extrahieren
        except json.JSONDecodeError:
            LOGGER.error("Fehler: Die Antwort ist kein gültiges JSON")
            json_data = None
    else:
        LOGGER.error(f"Fehler: HTTP-Statuscode {response.status_code}")
        json_data = None
    # print(json_data)
    return json_data

def filter_and_delete_usergroups(JAMF_URL, token, PREFIX, json_data):
    """
    Alle Benutzergrupoen mit einem bestimmten Präfix werden aus
    den übergebenen JSON-Benutzergruppendaten herausgefiltert
    und Schritt für Schritt gelöscht.
    Nur Hilfsfunktion für loesche_usergroups_mit_prefix (mit kompakterer Signatur)
    """
    filtered_usergroups = []
    id_list = []
    for c in json_data.get("user_groups", []):
        name = c.get("name")
        if(name[:len(PREFIX)]==PREFIX):
          class_id = c.get("id")
          filtered_usergroups.append(c)
          id_list.append(class_id)  # Füge die ID zur Liste hinzu
    #print(id_list)
    count = 0
    for i in range(len(id_list)):
        if count == 10:
            count = 0
            token = refresh_token(JAMF_URL, token)
        url = f"{JAMF_URL}/JSSResource/usergroups/id/{id_list[i]}"
        headers = {
            "Content-Type": "application/xml",
            "Accept": "application/xml",
            "Authorization": f"Bearer {token}"
        }
        response = requests.delete(url, headers=headers)
        if response.status_code in (200,201):
            count+=1
            LOGGER.info(id_list[i])
            LOGGER.info("Usergroup erfolgreich gelöscht!")
        else:
            LOGGER.error(f"Fehler beim Löschen: {response.text}")

def loesche_usergroups_mit_prefix(JAMF_URL,TOKEN, PREFIX):
    """löscht alle Benutzergruppen von JAMF, die ein bestimmtes Präfix haben."""
    token=TOKEN
    usergroups=get_usergroups(JAMF_URL, token)
    filter_and_delete_usergroups(JAMF_URL, token, PREFIX, usergroups)
    LOGGER.info("Löschen abgeschlossen")


