# beautify.py
import json
from jamfscripts.logging_config import LOGGER
from jamfscripts.big_class_merge import extract_courses

def read_json_file():
    file_path = "../daten/merged_schueler.json"  # Ersetze diesen Pfad mit dem tatsächlichen Pfad
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        LOGGER.error(f"Datei nicht gefunden: {file_path}")
    except json.JSONDecodeError:
        LOGGER.error(f"Fehler beim Dekodieren der JSON-Datei: {file_path}")
    except Exception as e:
        LOGGER.error(f"Ein unerwarteter Fehler ist aufgetreten: {e}")


# Beispielaufruf
data = read_json_file()
courses, student_classes = extract_courses(data)
