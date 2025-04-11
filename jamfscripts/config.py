import json
import os
from platformdirs import user_documents_dir, user_data_dir

config_dir = user_data_dir("Classload", "chribdo")
os.makedirs(config_dir, exist_ok=True)
CONFIG_FILE  = os.path.join(config_dir, "config.json")

DATA_DIR = os.path.join(user_documents_dir(), "Classload")
os.makedirs(DATA_DIR, exist_ok=True)

DEFAULT_CONFIG = {
    "INPUT_FILENAME": os.path.join(DATA_DIR, "iserv_schueler.json"),
    "TEACHER_GROUP_NAME": "",
    "OUTPUT_FILE_CLASSES": os.path.join(DATA_DIR, "alle_klassen.json"),
    "OUTPUT_FILE_STUDENTS": os.path.join(DATA_DIR, "merged_schueler.json"),
    "INPUT_DELETE_FILENAME": os.path.join(DATA_DIR, "delete_users.json"),
    "POSTFIX": "",
    "SITE_ID": "",
    "TEACHER_POSTFIX": "Nicht festgelegt"
}

def load_config():
    """Lädt die Konfiguration aus der JSON-Datei oder setzt Standardwerte."""
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)  # Falls Datei nicht existiert, Standardwerte speichern

    with open(CONFIG_FILE, "r") as file:
        return json.load(file)

def save_config(config):
    """Speichert die Konfiguration in die JSON-Datei."""
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=4)

def set_config_value(key, value):
    """Setzt einen einzelnen Konfigurationswert und speichert die Datei."""
    config = load_config()
    config[key] = value
    save_config(config)

def get_config_value(key):
    """Holt einen Konfigurationswert oder gibt None zurück, falls nicht vorhanden."""
    return load_config().get(key, None)

