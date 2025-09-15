import requests
import xml.etree.ElementTree as ET
import jamfscripts
from jamfscripts import get_config_value, refresh_token, get_site_id
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


############### Ab hier alles für den Button Mobilgerätegruppe hochladen ######


def simple_quote(s: str) -> str:
    return (s.replace(" ", "%20")
             .replace("/", "%2F")
             .replace("?", "%3F")
             .replace("#", "%23")
             .replace("&", "%26"))
def _name_lookup(jamf_url: str, token: str, group_name: str):
    headers = {"Accept": "application/xml", "Authorization": f"Bearer {token}", "Cache-Control": "no-cache", "Pragma": "no-cache"}
    url = f"{jamf_url}/JSSResource/mobiledevicegroups/name/{simple_quote(group_name)}"
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        return None
    try:
        root = ET.fromstring(r.text)
        el = root.find("./id")
        return int(el.text) if el is not None and el.text and el.text.isdigit() else None
    except ET.ParseError:
        return None



def _read_serials(csv_path: str) -> list[str]:
    serials = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.reader(f):
            if not row:
                continue
            s = (row[0] or "").strip()
            if not s or s.lower() in {"serial", "serialnumber", "serial_number", "seriennummer"}:
                continue
            if s.startswith("S"):
                s = s[1:]
            serials.append(s.upper())
    return sorted(set(serials))


#from xml.sax.saxutils import escape

def xml_escape(s: str) -> str:
    """Wandelt &, <, >, " und ' in XML-Entities um (ohne Imports)."""
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
         .replace('"', "&quot;")
         .replace("'", "&apos;")
    )

def create_group_with_members_from_csv(jamf_url: str, token: str, group_name: str, csv_path: str):
    """
    Legt die statische Mobile-Device-Gruppe 'group_name' nur dann neu an, wenn sie noch nicht existiert.
    Falls bereits vorhanden, Ausgabe einer Fehlermeldung und Rückgabe None.
    Ansonsten werden alle Geräte aus der CSV in EINEM POST mitgeschickt.
    Rückgabe: neue Gruppen-ID oder None.

    Abhängigkeiten: requests, xml.etree.ElementTree (Standardbibliothek)
    Kein time, kein re.
    """
    clean_name = group_name.strip()
    LOGGER.info("Vorgang gestartet. Bitte etwas Geduld...")
    # Bereits vorhandene Gruppe prüfen – wenn vorhanden, abbrechen
    existing_id = _name_lookup(jamf_url, token, clean_name)
    if existing_id is not None:
        LOGGER.error(f"❌ Gruppe '{clean_name}' existiert bereits (ID {existing_id}). Es wurden keine Änderungen vorgenommen.")
        return None

    # Serials laden
    serials = _read_serials(csv_path)
    if not serials:
        LOGGER.error("ℹ️ Keine gültigen Seriennummern gefunden.")
        return None

    # Site ermitteln
    site_id = get_site_id(jamf_url, token)

    # XML vorbereiten
    headers = {
        "Accept": "application/xml",
        "Content-Type": "application/xml",
        "Authorization": f"Bearer {token}",
    }
    url = f"{jamf_url}/JSSResource/mobiledevicegroups/id/0"

    devices_xml = "\n".join(
        f"<mobile_device><serial_number>{xml_escape(s)}</serial_number></mobile_device>"
        for s in serials
    )
    xml_body = f"""<mobile_device_group>
  <name>{xml_escape(clean_name)}</name>
  <is_smart>false</is_smart>
  <site><id>{site_id}</id></site>
  <mobile_devices>
    {devices_xml}
  </mobile_devices>
</mobile_device_group>""".strip()

    # POST (ohne Retry/Delay)
    r = requests.post(url, headers=headers, data=xml_body.encode("utf-8"))

    if r.status_code in (200, 201):
        # 1) ID aus Location-Header (ohne regex)
        loc = r.headers.get("Location") or r.headers.get("location")
        if loc:
            gid = _extract_id_from_location(loc)
            if gid is not None:
                LOGGER.info(f"✅ Gruppe '{clean_name}' erstellt (ID: {gid}) – Mitglieder direkt gesetzt ({len(serials)}).")
                return gid

        # 2) Fallback: ID aus Response-XML
        try:
            root = ET.fromstring(r.text)
            el = root.find("./id")
            if el is not None and el.text and el.text.isdigit():
                gid = int(el.text)
                LOGGER.info(f"✅ Gruppe '{clean_name}' erstellt (ID: {gid}) – Mitglieder direkt gesetzt ({len(serials)}).")
                return gid
        except ET.ParseError:
            pass

        LOGGER.error("⚠️ Gruppe erstellt, aber keine ID ermittelbar.")
        return None

    if r.status_code == 409:
        # Duplicate Name o.ä. – ohne Retry direkt abbrechen
        LOGGER.error(f"❌ Gruppe '{clean_name}' konnte nicht erstellt werden (409 Duplicate Name).")
        return None

    # Andere Fehler
    LOGGER.error(f"❌ Erstellen fehlgeschlagen ({r.status_code}): {r.text[:400]}")
    return None


def _extract_id_from_location(loc: str):
    """
    Extrahiert eine numerische ID aus einem Location-Header rein über String-Operationen.
    Beispiel: .../mobiledevicegroups/id/123 -> 123
    """
    # letzten Pfadteil nehmen
    tail = loc.rstrip("/").split("/")[-1]
    # Falls der letzte Teil nicht numerisch ist (z.B. 'id'), noch den vorletzten prüfen
    candidate_parts = [tail]
    if tail.lower() == "id" and "/" in loc:
        candidate_parts.append(loc.rstrip("/").split("/")[-2])

    for part in candidate_parts:
        # Ziffern am Ende extrahieren (ohne re): rückwärts sammeln
        digits_rev = []
        for ch in reversed(part):
            if ch.isdigit():
                digits_rev.append(ch)
            else:
                # sobald keine Ziffer mehr, stoppen (wir wollen den abschließenden Ziffernblock)
                if digits_rev:
                    break
        if digits_rev:
            try:
                return int("".join(reversed(digits_rev)))
            except ValueError:
                pass
    return None
