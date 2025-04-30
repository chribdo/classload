# 👩‍🏫 Classload

**Classload** ist hilfreich bei der Verwaltung von Mobilgeräten, Benutzern, Benutzergruppen und vor allem Klassen mit JAMF.

So schön kann Jamf (mit Classload) organisiert sein: 
- Die Mobilgerätenamen beinhalten die Klarnamen der Nutzer:innen, sodass bei Airdrops direkt klar ist, wer welche Datei versendet hat.
- Der Asset-Tag (in Dortmund IT-Nummer) ist bei allen Geräten eingetragen, sodass man Geräte in JAMF auch darüber leicht finden kann.
- Allen Lehrer- und Schüler-Geräten sind Benutzer mit Klarnamen zugeordnet. In der Classroom-App sieht dadurch dann später alles schön übersichtlich aus.
- **Zu jedem Unterricht in Webuntis gibt es eine Gruppe in iServ und zu jeder Gruppe in iServ gibt es eine korrespondierende Classroom-Klasse und bei Bedarf auch eine statische Mobilgeräte-Gruppe. Classload ermöglicht letzteres, wenn sowohl Webuntis als auch iServ verwendet werden und Unterrichte mit dem Webuntis Connector synchronisieren.**
- (Bluetooth ändern ist deaktiviert, damit Schüler:innen sich der Classroom-App weniger leicht entziehen können).

## 🖼️ Screenshot

![Screenshot](screenshot.png)

## ✨ Funktionen

Das Programm startet mit der Eingabe von Benutzername und Passwort sowie der Adresse der (eigenen) JAMF-Instanz. Danach stehen Buttons mit folgenden Funktionen zur Verfügung: 

- **Konfiguration**: Hier werden Werte eingetragen, mit denen das Programm arbeitet.
    - Statische Benutzergruppe aller Lehrkräfte in JAMF: In JAMF sollte eine (statische) Benutzergruppe angelegt werden, der (zum aktuellen Zeitpunkt oder später) alle Benutzer angehören, die Lehrkräfte sind. Der Name dieser Gruppe **muss hier eingetragen werden**. Alle anderen Veränderungen von Werten sind optional und sollten im Zweifelsfall lieber unterlassen werden.
    - SITE-ID: Die SITE-ID wird auf Grundlage des Accounts automatisch ermittelt. Eine JAMF-Instanz kann mehrere Sites (z.B. für mehrere Schulen) haben.
    - Pfade zur Ausgabe: Es gibt automatische Vorschläge, die bei Bedarf abgeändert werden können. In diese Verzeichnisse werden Dateien geschrieben, die zur Kontrolle vor dem eigentlichen Klassen-Upload genutzt werden können.
    - Mögliches Postfix für JAMF-Schüler-Benutzer: Schüler können bei Bedarf ein Postfix erhalten, also statt 'Betty Beispiel' z.B. 'Betty Beispiel RSG'. Das führende Leerzeichen sollte, falls gewünscht, nicht vergessen werden. Standardmäßig wird dieses Postfix nicht verwendet, selbst wenn es eingetragen ist. Die Zuordnung funktioniert damit jedoch.
    - Lehrkräfte-POSTFIX: Um Lehrerbenutzer in JAMF schnell erkennen zu können, erhalten sie standardmäßig ein Postfix. Bei uns am RSG wird aus 'Betty Beispiel' z.B. 'Betty Beispiel RSGL'.
- **Schüler:innen-iPads zuordnen**: Als Eingabe wird eine csv mit drei Spalten benötigt: Vorname; Nachname; Seriennummer. Als Trennzeichen wird ein Semikolon erwartet, Spaltenüberschriften soll es nicht geben, bei der Seriennummer ist es egal ob vorne ein S steht oder nicht. In Dortmund kann man diese Daten einfach aus der Excel-Tabelle, die man für die Verträge sowieso verwaltet, kopieren und aus Excel oder ähnlichen Programmen als csv exportieren. **Wenn man die Datei ausgewählt hat, werden die Geräte automatisch umbenannt und erhalten einen Benutzer mit passendem Namen.**
- **Lehrkräfte-iPads zuordnen**: Als Eingabe wird eine csv mit drei Spalten benötigt: Vorname; Nachname; Lehrerkürzel (eindeutig); Seriennummer. Als Trennzeichen wird ein Semikolon erwartet, Spaltenüberschriften soll es nicht geben, bei der Seriennummer ist es egal ob vorne ein S steht oder nicht. **Wenn man die Datei ausgewählt hat, werden die Geräte automatisch umbenannt und erhalten einen Benutzer mit passendem Namen. Das Lehrerkürzel wird bei der Telefonnummer eingetragen (sic!). Außerdem werden die Lehrkräfte der Benutzergruppe der Lehrkräfte hinzugefügt.**
- **IT-Nummern/Asset-Tags hochladen**: Als Eingabe wird eine csv mit zwei Spalten benötigt: Asset-Tag (=IT-Nummer); Seriennummer. Als Trennzeichen wird ein Semikolon erwartet, Spaltenüberschriften soll es nicht geben, bei der Seriennummer ist egal ob vorne ein S steht oder nicht.
- Auf Grundlage von CSV-Dateien können Geräten Benutzernamen und neue Gerätenamen zugewiesen werden.
- Classroom-Klassen können auf Grundlage von iServ-Daten erstellt werden – vorausgesetzt, WebUntis wird ebenfalls genutzt **und** iServ und WebUntis synchronisieren bereits die Unterrichte.  
  Mehr dazu z. B. [hier](https://help.untis.at/hc/de/articles/4411822372754-Plattform-Applikation-IServ) oder [hier](https://doku.iserv.de/manage/user/webuntis/).
- Benutzer ohne Mobilgerät können einfach aus JAMF gelöscht werden.
- Weitere nützliche Funktionen rund um Klassen- und Benutzergruppenverwaltung.

## 💻 Voraussetzungen

- Es gibt Versionen für Windows und macOS.
- Eine Linux-Version ist ebenfalls verfügbar (ungetestet).

## 🧑‍💻 Autorin

Classload wurde entwickelt von Dr. Christiane Borchel, Lehrerin am Reinoldus- und Schiller-Gymnasium in Dortmund.

## 📄 Lizenz

Die Nutzung ist ausschließlich für den privaten und schulischen Bereich erlaubt.  
Die kommerzielle Nutzung oder die Nutzung durch Schulträger ist lediglich im Rahmen einer Testversion gestattet.  
Genaueres ist in der Datei [LICENSE.txt](LICENSE.txt) geregelt.
