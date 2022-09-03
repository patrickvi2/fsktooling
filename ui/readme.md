# DEUMeldeformularKonverter

## Zweck
Das Tool extrahiert Informationen aus der DEU-Meldeliste (xlsx-Format) und konvertiert diese Daten in verschiedene andere Formate, 
um manuelles Übertragen der Personen-Daten zu minimieren.

## Wettbewerbe
Für Wettbewerbe kann das Meldeformular nach [ODF](https://odf.olympictech.org/project.htm) konvertiert werden, 
welches vom FS Manager gelesen werden kann.

### Anleitung
1. Im DEUMeldeformularKonverter
    - Excel-Datei auswählen
    - auf konvertieren klicken
    - neben dem ausgewählten Meldeformular werden die ODF-Dateien `DT_PARTIC.xml` und `DT_PARTIC_TEAM.xml` generiert 
2. Im FS Manager
    - neue Datenbank erstellen
    - Elemente aus FSM masterData einlesen
    - Clubs und Nations aus DEUMeldeformularKonverter einlesen (./masterData/FSM/*.xml)
    - Flaggen kopieren 
        * ./masterData/FSM/flags/copyToFSM.bat ausführen
        * Alternativ die Flaggen von Hand im FSM hinzufügen
    - Kategorien einlesen
        * Time Schedule > "Import Categories / Segments"
        * erzeugte `DT_PARTIC.xml` auswählen
    - Personen einlesen
        * People > Import > Initial Download (complete)
        * erzeugte `DT_PARTIC.xml` auswählen
    - Paare & Eistänzer
        * Couples > Import > Initial Download (complete)
        * erzeugte `DT_PARTIC_TEAMS.xml` auswählen
    - Synchron-Teams einlesen
        * Synchornized Teams > Import > Initial Download (complete)
        * erzeugte `DT_PARTIC_TEAMS.xml` auswählen
 
### Einschränkungen
1. Kategorienamen können nicht importiert werden
2. Non-ISU-Kategorien werden als Senioren-Klasse angelegt
3. alle Nachwuchskategorien werden "Advanced Novice" zugeordnet
    - "Basic Novice" -> beginnt der Kategoriename mit "Basic Novice"
    - "Intermediate Novice" -> beginnt der Kategoriename mit "Intermediate Novice"
4. Jugendklasse wird der Juniorenklasse zugeordnet
5. Synchronteams können keine Athleten zugeordnet werden
