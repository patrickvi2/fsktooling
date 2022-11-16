import mysql.connector
import csv
from xml.etree import ElementTree as ET

con = mysql.connector.connect(user='sa', password='fsmanager', host='127.0.0.1', database='database')
output_csv_file_name = "result.csv"

cursor = con.cursor()

processed_categories = []
data = list()
data.append(["Wettbewerb/Prüfung",
             "Team ID",
             "Team Name",
             "ID ( ehm. Sportpassnr.)",
             "Name",
             "Vorname",
             "Geb. Datum",
             "Vereinskürzel",
             "Rolle",
             "Platz/Status",
             "Punkte"
])

# participant result from ODF messages
cursor.execute("SELECT Id, Message, OdfMessageType, Version, CreationStamp "
               "FROM odfmessage "
               "WHERE OdfMessageType = \"DT_CUMULATIVE_RESULT\" "
               "ORDER BY CreationStamp DESC")
for (odf_id, odf_message, odf_type, odf_message_version, odf_stamp) in list(cursor):
    root = ET.fromstring(odf_message)
    desc = root.find("Competition/ExtendedInfos/SportDescription")
    cat_name = desc.attrib["EventName"]

    if cat_name in processed_categories:
        continue

    print(cat_name)
    processed_categories.append(cat_name)

    for result in root.findall("Competition/Result"):
        rank = ""
        points = ""
        if "Rank" not in result.attrib:
            rank = "zurückgezogen"
        else:
            rank = result.attrib["Rank"]
            points = result.attrib["Result"]
        athletes = list(result.findall("Competitor/Composition/Athlete/Description"))
        team_id = ""
        if not athletes:
            # sys team
            res_desc = result.find("Competitor/Description")
            a = res_desc.attrib
            d = [cat_name, a["IFId"], a["TeamName"], "", "", "", "", "", "TN", rank, points]
            print(d)
            data.append(d)
        elif len(athletes) == 2:
            # team id for pairs / dance
            team_id = "-".join([athlete.attrib["IFId"] for athlete in athletes])
        for athlete in athletes:
            a = athlete.attrib
            d = [cat_name, team_id, "", a["IFId"], a["FamilyName"], a["GivenName"], a["BirthDate"], a["Organisation"], "TN", rank, points]
            print(d)
            data.append(d)


map_officials_from_FSM_to_DEU = {0 : "SR",
                                 1 : "PR",
                                 2 : "TC",
                                 3 : "TS",
                                 4 : "TI",
                                 5 : "DO",
                                 6 : "RO"}

official_data = set()
# get officials from categories and segments
cursor.execute("SELECT Id, Name, Level, Type, SortOrder FROM category")
for (cat_id, cat_name, cat_level, cat_type, cat_order) in list(cursor):
    cursor.execute("SELECT Id, Name, ShortName, SegmentType FROM segment WHERE Category_Id = " + str(cat_id))
    print(cat_name)

    for (seg_id, seg_name, seg_short_name, seg_type) in list(cursor):
        cursor.execute("SELECT person.FederationId, person.FirstName, person.LastName, person.BirthDate, officialinsegment.OfficialFunction "
                       "FROM officialinsegment "
                       "    JOIN person ON person.id = officialinsegment.Person_Id "
                      f"WHERE officialinsegment.Segment_Id = {str(seg_id)} ")
        print(seg_name)

        for (fed_id, first_name, last_name, birthday, function) in list(cursor):
            d = (cat_name, "", "", fed_id, last_name, first_name, birthday, "", map_officials_from_FSM_to_DEU[function], "", "")
            print(d)
            official_data.add(d)

data.extend([list(d) for d in official_data])

# close database connection
con.close()

# write csv data
with open(output_csv_file_name, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(data)

