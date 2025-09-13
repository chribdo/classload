import requests
import xml.etree.ElementTree as ET
import jamfscripts
from jamfscripts import get_config_value, refresh_token
from jamfscripts.logging_config import LOGGER
import csv

def create_asset_xml(asset_tag):
    """gibt eine Asset- Information als XML-String zurück"""
    top_element = ET.Element("mobile_device")
    general_element = ET.SubElement(top_element, "general")
    it_n_element = ET.SubElement(general_element, "asset_tag")
    it_n_element.text = asset_tag
    return ET.tostring(top_element, encoding="utf-8").decode("utf-8")

def create_mobile_device_xml(geraetename, benutzername, asset_tag=None, phone=None ):   #### Upload einzelner Gruppe
    """gibt einen XML-String für ein einzelnes Mobilgerät (für Schüler) zurück"""
    top_element = ET.Element("mobile_device")

    general_element = ET.SubElement(top_element, "general")

    display_n_element = ET.SubElement(general_element, "display_name")
    display_n_element.text = geraetename

    device_n_element = ET.SubElement(general_element, "device_name")
    device_n_element.text = geraetename

    # >>> EINZIGE ANPASSUNG <<<
    enforce_element = ET.SubElement(general_element, "enforce_mobile_device_name")
    enforce_element.text = "true"
    # <<< EINZIGE ANPASSUNG <<<

    n_element = ET.SubElement(general_element, "name")
    n_element.text = geraetename

    location_element = ET.SubElement(top_element, "location")

    username_element = ET.SubElement(location_element, "username")
    username_element.text = benutzername

    real_n_element = ET.SubElement(location_element, "realname")
    real_n_element.text = benutzername
    real_n_element1 = ET.SubElement(location_element, "real_name")
    real_n_element1.text = benutzername
    email_element = ET.SubElement(location_element, "email_address")
    email_element.text = benutzername

    real_n_element = ET.SubElement(location_element, "realname")
    real_n_element.text = benutzername
    if (asset_tag != None):
        it_n_element = ET.SubElement(general_element, "asset_tag")
        it_n_element.text = asset_tag

    if (phone != None):
        phone_element = ET.SubElement(location_element, "phone")
        phone_element.text = phone

    return ET.tostring(top_element, encoding="utf-8").decode("utf-8")

def create_teacher_device_xml(geraetename, lehrername, kuerzel):   #### Hier WEITERMACHEN!!!!!!!!!!!!!! Upload einzelner Gruppe
    """
    gibt einen XML-String für ein einzelnes Lehrkräfte-Mobilgerät zurück.
    Dabei wird auch das Kürzel berücksichtigt und unter anderem als Telefonnummer eingetragen.
    Das war bei der Implementierung leider praktisch ;)
    """
    top_element = ET.Element("mobile_device")

    general_element = ET.SubElement(top_element, "general")

    display_n_element = ET.SubElement(general_element, "display_name")
    display_n_element.text = geraetename

    device_n_element = ET.SubElement(general_element, "device_name")
    device_n_element.text = geraetename

    # >>> EINZIGE ANPASSUNG <<<
    enforce_element = ET.SubElement(general_element, "enforce_mobile_device_name")
    enforce_element.text = "true"
    # <<< EINZIGE ANPASSUNG <<<

    n_element = ET.SubElement(general_element, "name")
    n_element.text = geraetename

    location_element = ET.SubElement(top_element, "location")

    username_element = ET.SubElement(location_element, "username")
    username_element.text = lehrername

    real_n_element = ET.SubElement(location_element, "realname")
    real_n_element.text = lehrername
    real_n_element1 = ET.SubElement(location_element, "real_name")
    real_n_element1.text = lehrername
    email_element = ET.SubElement(location_element, "email_address")
    email_element.text = lehrername

    real_n_element = ET.SubElement(location_element, "realname")
    real_n_element.text = lehrername
    phone_element = ET.SubElement(location_element, "phone")
    phone_element.text = kuerzel

    return ET.tostring(top_element, encoding="utf-8").decode("utf-8")

def upload_device_information_OLD(jamf_url, token, serial, geraetename, benutzername, asset_tag=None, phone=None):
    """
    Veraltet: Schueler-Geräte werden gemäß einer csv-Liste aktualisiert.
    Die Geräte erhalten einen neuen Namen und einen neuen Benutzer.
    Die Namen ergeben sich so: "Vorname Name" bzw. "Vorname Name Postfix"
    zum Postfix siehe config.json bzw. Konfigurationsdialog.
    """
    LOGGER.info("Gerätezuordnung gestartet..")
    xml_string = create_mobile_device_xml(geraetename, benutzername, asset_tag, phone)

    url = f"{jamf_url}/JSSResource/mobiledevices/serialnumber/{serial}"
    headers = {"Content-Type": "application/xml",
               "Accept": "application/xml",
               "Authorization": f"Bearer {token}"
               }
    #print(xml_string)
    #LOGGER.info("Gerät wird aktualisiert. Das kann etwas dauern..")
    response = requests.put(url, headers=headers, data=xml_string)
    #response = requests.get(url, headers=headers)
    if response.status_code in (200, 201):
        print(response.text)
        LOGGER.info("Upload erfolgreich!")
    else:
        LOGGER.info(response.status_code)
        LOGGER.error(f"Fehler beim Put: {response.text}")

def get_mobile_id_by_serial(jamf_url: str, token: str, serial: str):
    """gibt bei Erfolg die ID des Mobilgeräts zu einer Seriennummer zurück, sonst None."""
    h = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    url = f"{jamf_url.rstrip('/')}/JSSResource/mobiledevices/serialnumber/{serial.strip()}"
    r = requests.get(url, headers=h, timeout=15)
    if not r.ok:
        print(r.status_code, r.text[:300]); return None
    try:
        j = r.json()
    except ValueError:
        print("Non-JSON:", r.text[:300]); return None

    md = j.get("mobile_device")
    if isinstance(md, dict):
        return md.get("id") or (md.get("general") or {}).get("id")

    lst = (j.get("mobile_devices") or {}).get("mobile_device") or []
    if lst and isinstance(lst[0], dict):
        x = lst[0]
        return x.get("id") or (x.get("general") or {}).get("id")

    print(j)  # Debug: zeig die echte Struktur
    return None

def upload_device_information(jamf_url: str, token: str, serial: str, geraete_name: str, schueler_name: str, ):
    """
    Setzt den Gerätenamen (v2) und aktualisiert Username/Realname im 'location'-Block.
    'displayName' gibt es im v2-PATCH nicht; die UI verwendet i.d.R. den Realnamen als Anzeige.
    enforceName wird immer auf True gesetzt.
    Gibt True zurück, wenn erfolgreich.
    """
    base = jamf_url.rstrip("/")
    device_id = get_mobile_id_by_serial(jamf_url, token, serial)
    url = f"{base}/api/v2/mobile-devices/{device_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    payload = {
        "name": geraete_name,
        "enforceName": True,  # immer aktiv
        "location": {
            "username": schueler_name,
            "realName": schueler_name,
        },
    }

    r = requests.patch(url, headers=headers, json=payload)
    if r.status_code in (200, 204):
        LOGGER.info("Geräte- und Benutzername erfolgreich aktualisiert")
    else:
        LOGGER.error("Fehler bei der Aktualisierung der Geräteinformationen")


def upload_teacher_device_information_(jamf_url, token, serial, lehrer_name, kuerzel):
    """
    Ein Lehrer-iPad erhält einen neuen Namen, einen neuen Benutzer mit Name und Kürzel (wird anstelle der Telefonnummer eingesetzt).
    Außerdem wird die Lehrkraft der Lehrkräfte-Benutzergruppe hinzugefügt.
    """


    """
    ################ Veraltet:
    LOGGER.info("Gerätezuordnung gestartet..")
    teacher_postfix=get_config_value("TEACHER_POSTFIX")
    geraetename=lehrer_name+teacher_postfix
    lehrername_postfix = lehrer_name+teacher_postfix
    
    xml_string = create_teacher_device_xml(geraetename, lehrername_postfix, kuerzel)
    url = f"{jamf_url}/JSSResource/mobiledevices/serialnumber/{serial}"
    headers = {"Content-Type": "application/xml",
               "Accept": "application/xml",
               "Authorization": f"Bearer {token}"
               }
    #print(xml_string)
    #LOGGER.info("Gerät wird aktualisiert. Das kann etwas dauern..")
    response = requests.put(url, headers=headers, data=xml_string)
    #response = requests.get(url, headers=headers)
    
    #################################
    """

    LOGGER.info("Gerätezuordnung gestartet..")
    teacher_postfix = get_config_value("TEACHER_POSTFIX")
    geraete_name = lehrer_name + teacher_postfix
    lehrername_postfix = lehrer_name + teacher_postfix
    base = jamf_url.rstrip("/")
    device_id = get_mobile_id_by_serial(jamf_url, token, serial)
    url = f"{base}/api/v2/mobile-devices/{device_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    payload = {
        "name": geraete_name,
        "enforceName": True,  # immer aktiv
        "location": {
            "username": lehrername_postfix,
            "realName": lehrer_name,
            "phoneNumber": kuerzel,
            "emailAddress": lehrername_postfix,
            "position": kuerzel
        },
    }

    response = requests.patch(url, headers=headers, json=payload)

    if response.status_code in (200, 201):
        print(response.text)
        LOGGER.info("Upload erfolgreich!")
        teacher_group_name=get_config_value("TEACHER_GROUP_NAME")
        jamfscripts.update_teacher_group(jamf_url, token, teacher_group_name, lehrername_postfix)
        if response.status_code in (200, 201):
            #print(response.text)
            LOGGER.info("OK")
        else:
            LOGGER.info(response.status_code)
            LOGGER.error(f"Lehrkraft konnte der Lehrergruppe nicht hinzugefügt werden: {response.text}")
    else:
        LOGGER.info(response.status_code)
        LOGGER.error(f"Fehler beim Patch: {response.text}")

def upload_asset_information(jamf_url, token, serial, asset_tag):
        """Die Asset-Information zu einem einzelnen Mobilgerät wird zu JAMF hochgeladen."""
        LOGGER.info("Gerätezuordnung gestartet..")
        xml_string = create_asset_xml( asset_tag)
        url = f"{jamf_url}/JSSResource/mobiledevices/serialnumber/{serial}"
        headers = {"Content-Type": "application/xml",
                   "Accept": "application/xml",
                   "Authorization": f"Bearer {token}"
                   }
        # print(xml_string)
        #LOGGER.info("Gerät wird aktualisiert. Das kann etwas dauern..")
        response = requests.put(url, headers=headers, data=xml_string)
        # response = requests.get(url, headers=headers)
        if response.status_code in (200, 201):
            print(response.text)
            LOGGER.info("Upload erfolgreich!")
        else:
            LOGGER.info(response.status_code)
            LOGGER.error(f"Fehler beim Put: {response.text}")

def it_nummern_hochladen(jamf_url, token, pfad_zur_csv):
    """Mehrere Asset-Informationen zu Geräten werden zu JAMF hochgeladen."""
    with open(pfad_zur_csv, 'r', encoding='utf-8-sig', newline='') as f:
        # BOM wird durch utf-8-sig automatisch entfernt
        sample = f.read(1024)
        f.seek(0)

        # Trennzeichen automatisch erkennen
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(sample)

        reader = csv.reader(f, dialect)
        i = 4
        LOGGER.info("Die Geräte werden aktualisiert...")
        for zeile in reader:
            i+=1
            if (i % 5==0):
                token=refresh_token(jamf_url, token)
            if len(zeile) < 2:
                continue  # Zeile überspringen, wenn nicht genug Spalten
            it_nummer = zeile[0].strip()
            seriennummer = zeile[1].strip()
            if seriennummer.startswith("S"):
                seriennummer = seriennummer[1:]
            upload_asset_information(jamf_url, token, seriennummer, it_nummer)

def schueler_ipads_aktualisieren(jamf_url, token, pfad_zur_csv):
    """
    Schueler-Geräte werden gemäß einer csv-Liste aktualisiert.
    Die Geräte erhalten einen neuen Namen und einen neuen Benutzer.
    Die Namen ergeben sich so: "Vorname Name" bzw. "Vorname Name Postfix"
    zum Postfix siehe config.json bzw. Konfigurationsdialog.
    """
    with open(pfad_zur_csv, 'r', encoding='utf-8-sig', newline='') as f:
        # BOM wird durch utf-8-sig automatisch entfernt
        sample = f.read(1024)
        f.seek(0)

        # Trennzeichen automatisch erkennen
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(sample)

        reader = csv.reader(f, dialect)
        LOGGER.info("Die Geräte werden aktualisiert...")
        i = 1
        for zeile in reader:
            LOGGER.info("Gerät Nr. "+str(i)+ " wird bearbeitet...")
            i+=1
            if (i % 5==0):
                token=refresh_token(jamf_url, token)
            if len(zeile) < 3:
                continue  # Zeile überspringen, wenn nicht genug Spalten

            vorname = zeile[0].strip()
            nachname = zeile[1].strip()
            seriennummer = zeile[2].strip()

            if seriennummer.startswith("S"):
                seriennummer = seriennummer[1:]

            name = f"{vorname} {nachname}"
            geraetename = name + get_config_value("POSTFIX")

            upload_device_information(jamf_url, token, seriennummer, geraetename, name)
    LOGGER.info("Bearbeitung aller Geräte abgeschlossen.")

def lehrer_ipads_aktualisieren(jamf_url, token, pfad_zur_csv):
    """
    Lehrer-Geräte werden gemäß einer csv-Liste aktualisiert.
    Die Geräte erhalten einen neuen Namen und einen neuen Benutzer.
    """
    with open(pfad_zur_csv, 'r', encoding='utf-8-sig', newline='') as f:
        # BOM wird durch utf-8-sig automatisch entfernt
        sample = f.read(1024)
        f.seek(0)

        # Trennzeichen automatisch erkennen
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(sample)

        reader = csv.reader(f, dialect)
        LOGGER.info("Die Geräte werden aktualisiert...")
        i = 1
        for zeile in reader:
            LOGGER.info("Gerät Nr. "+ str(i)+ " wird bearbeitet.")
            i+=1
            if (i % 5==0):
                token=refresh_token(jamf_url, token)
            if len(zeile) < 3:
                continue  # Zeile überspringen, wenn nicht genug Spalten

            vorname = zeile[0].strip()
            nachname = zeile[1].strip()
            kuerzel = zeile[2].strip()
            seriennummer = zeile[3].strip()

            if seriennummer.startswith("S"):
                seriennummer = seriennummer[1:]

            name = f"{vorname} {nachname}"
            upload_teacher_device_information_(jamf_url, token, seriennummer, name, kuerzel)
        LOGGER.info("Bearbeitung aller Geräte abgeschlossen.")

