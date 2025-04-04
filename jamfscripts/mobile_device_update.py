#from benutzer_loeschen import *
import requests
import xml.etree.ElementTree as ET

import jamfscripts
from jamfscripts import get_config_value, refresh_token
from jamfscripts.logging_config import LOGGER
import csv

def create_asset_xml(asset_tag):
    top_element = ET.Element("mobile_device")
    general_element = ET.SubElement(top_element, "general")
    it_n_element = ET.SubElement(general_element, "asset_tag")
    it_n_element.text = asset_tag
    return ET.tostring(top_element, encoding="utf-8").decode("utf-8")

def create_mobile_device_xml(geraetename, benutzername, asset_tag=None, phone=None ):   #### Hier WEITERMACHEN!!!!!!!!!!!!!! Upload einzelner Gruppe
    top_element = ET.Element("mobile_device")

    general_element = ET.SubElement(top_element, "general")

    display_n_element = ET.SubElement(general_element, "display_name")
    display_n_element.text = geraetename

    device_n_element = ET.SubElement(general_element, "device_name")
    device_n_element.text = geraetename

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
    top_element = ET.Element("mobile_device")

    general_element = ET.SubElement(top_element, "general")

    display_n_element = ET.SubElement(general_element, "display_name")
    display_n_element.text = geraetename

    device_n_element = ET.SubElement(general_element, "device_name")
    device_n_element.text = geraetename

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

def upload_device_information_(jamf_url, token, serial, geraetename, benutzername, asset_tag=None, phone=None):
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

def upload_teacher_device_information_(jamf_url, token, serial, lehrer_name, kuerzel):
    # ein Lehrer-iPad erhält einen neuen Namen, einen neuen Benutzer mit Name und Kürzel (wird anstelle der Telefonnummer eingesetzt)
    # außerdem wird  der Lehrer der Lehrkräfte-Benutzergruppe hinzugefügt.
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
        LOGGER.error(f"Fehler beim Put: {response.text}")

def upload_asset_information(jamf_url, token, serial, asset_tag):
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

            upload_device_information_(jamf_url, token, seriennummer, geraetename, name)

def lehrer_ipads_aktualisieren(jamf_url, token, pfad_zur_csv):
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

