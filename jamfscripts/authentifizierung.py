import requests, os
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from jamfscripts.logging_config import LOGGER
from jamfscripts import config,big_class_merge
from pathlib import Path

def get_cipher():
    """Holt einen (ggf. neuen) Schlüssel"""
    # 👉 env_file zuerst definieren
    env_file = Path.home() / ".Classload.env"

    # dann laden
    load_dotenv(dotenv_path=env_file)

    key = os.getenv("SECRET_KEY")

    if key is None:
        LOGGER.info("🔑 Kein Schlüssel gefunden. Generiere neuen...")

        key = Fernet.generate_key().decode()

        with open(env_file, "a") as f:
            f.write(f"SECRET_KEY={key}\n")

        LOGGER.info(f"✅ Neuer Schlüssel wurde erstellt in {env_file}")
    else:
        LOGGER.info("✅ Schlüssel geladen.")

    return Fernet(key.encode())

def get_auth_token(JAMF_URL, USERNAME, PASSWORD):
    """Holt ein Bearer-Token von der Jamf Pro API."""
    LOGGER.info("Hole Token")
    url = f"{JAMF_URL}/api/v1/auth/token"
    headers = {
        "Accept": "application/json"
    }
    response = requests.post(url, headers=headers, auth=(USERNAME, get_cipher().decrypt(PASSWORD)))
    if response.status_code == 200:

        LOGGER.info("Login erfolgreich. Token erhalten.")
        return response.json().get("token")
    else:
        LOGGER.error("Token nicht erhalten. Zugangsdaten prüfen.")
        return ""
        #raise Exception(f"Fehler beim Abrufen des Tokens: {response.text}")

def refresh_token(JAMF_URL, token):
    """Holt einen aufgefrischten Bearer-Token von der Jamf Pro API."""
    url = f"{JAMF_URL}/api/v1/auth/keep-alive"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
    response = requests.post(url, headers=headers)
    if response.status_code == 200:

        LOGGER.info("Token erfolgreich erneuert.")
        return response.json().get("token")
    else:
        LOGGER.error("Token nicht erhalten.")
        return ""
        #raise Exception(f"Fehler beim Abrufen des Tokens: {response.text}")


def initialisiere(JAMF_URL, TOKEN):
    """Standardwerte werden gesetzt, teilweise mithilfe der JAMF-API (z.B. SITE_ID)"""
    LOGGER.info("Initialisiere...")
    fetched_id = big_class_merge.get_site_id(JAMF_URL, TOKEN)
    fetched_name = big_class_merge.get_site_name(JAMF_URL, TOKEN)
    sid = config.get_config_value("SITE_ID")
    tpost = config.get_config_value("TEACHER_POSTFIX")
    #LOGGER.info(tpost)
    fehlermeldung = "Nicht importierbar"
    if (sid == "" or sid == fehlermeldung) :
        sid = fetched_id
        if (sid == None):
            sid = fehlermeldung
        config.set_config_value("SITE_ID", sid)

    if (tpost == "Nicht festgelegt" or tpost == fehlermeldung) :
        if (tpost!=""):
          tpost = " "+fetched_name+"L"
        if (tpost == None):
            tpost = fehlermeldung
        config.set_config_value("TEACHER_POSTFIX", tpost)

    name = config.get_config_value("SITE_NAME")
    fehlermeldung = "Nicht importierbar"
    if (name == "" or name == fehlermeldung):
        name = fetched_name
        if (name == None):
            name = fehlermeldung
        config.set_config_value("SITE_NAME", name)

    postfix = config.get_config_value("POSTFIX")
    if (postfix == "" or fetched_name == fehlermeldung):
        postfix = " "+fetched_name
        if (postfix == None):
            postfix = fehlermeldung
        config.set_config_value("POSTFIX", postfix)

    tgn = config.get_config_value("TEACHER_GROUP_NAME")
    if(name == None):
        name=""
    if (tgn == "" or tgn =="Lehrer L"):
        tgn = "Lehrer " + fetched_name + "L"
        if (tgn == None):
            tgn = ""
        config.set_config_value("TEACHER_GROUP_NAME", tgn)
    """
    ofc = config.get_config_value("OUTPUT_FILE_CLASSES")
    if (ofc == ""):
        ofc = "./daten/alle_klassen.json"
        config.set_config_value("OUTPUT_FILE_CLASSES", ofc)

    ofs = config.get_config_value("OUTPUT_FILE_STUDENTS")
    if (ofs == ""):
        ofs = "./daten/merged_schueler.json"
        config.set_config_value("OUTPUT_FILE_STUDENTS", ofs)
    """
    ifn = config.get_config_value("INPUT_FILENAME")
    if (ifn == ""):
        ifn = "./daten/iserv_schueler.csv"
        config.set_config_value("INPUT_FILENAME", ifn)

    idf = config.get_config_value("INPUT_DELETE_FILENAME")
    if (idf == ""):
        idf = "./daten/deleteUsers.csv"
        config.set_config_value("INPUT_DELETE_FILENAME", idf)

    LOGGER.info("✅ Initialisierung abgeschlossen.")

