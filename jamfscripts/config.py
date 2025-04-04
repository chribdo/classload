# config.py
import json
import os

CONFIG_FILE = "../config.json"

# Standardwerte für die Konfigurationsdatei
DEFAULT_CONFIG = {
    "SITE_ID": "",
    "POSTFIX": "",
    "INPUT_FILENAME": "./daten/iserv_schueler.csv",
    "TEACHER_GROUP_NAME": "",
    "OUTPUT_FILE_CLASSES": "./alle_klassen.json",
    "OUTPUT_FILE_STUDENTS": "./merged_schueler.json",
    "INPUT_DELETE_FILENAME": "./daten/deleteUsers.csv",
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
