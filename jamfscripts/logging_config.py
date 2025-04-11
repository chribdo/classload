import logging, os, tempfile
from rich.logging import RichHandler

LOG_FILE = os.path.join(tempfile.gettempdir(), "classload_error.log")
def setup_logger():
    """Konfiguriert den Logger. Geloggt wird in das temporäre Verzeichnis"""
    logger = logging.getLogger("rich_logger")
    logger.setLevel(logging.DEBUG)  # Setze Log-Level auf DEBUG

    # RichHandler für die Konsole
    console_handler = RichHandler()

    # FileHandler für die Logdatei
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(file_formatter)
    if os.path.isfile(LOG_FILE) and os.path.getsize(LOG_FILE) > 0:
        # Datei leeren
        with open(LOG_FILE, 'w') as file:
             pass  # Leere Datei erstellen
    # Falls bereits Handler existieren, diese zuerst entfernen (Vermeidung von doppelten Logs)
    if logger.hasHandlers():
        logger.handlers.clear()

    # Handler zum Logger hinzufügen
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger

# Initialisieren und global verfügbar machen
LOGGER = setup_logger()