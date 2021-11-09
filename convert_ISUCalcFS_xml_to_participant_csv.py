import xml.etree.ElementTree as ET
import csv

# settings / defines
isucalcfs_xml_file_path = "OBM22/xml/211030-OBM22-008.XML"
output_csv_file_path = "OBM22/csv/obm_starting_order_sa.csv"
reverse_birthday_date_format = True # format switch for birthday output in CSV file; False -> YYYYMMDD; True -> DDMMYYYY


# script code
tree = ET.parse(isucalcfs_xml_file_path)

root = tree.getroot()

output_list_dict = []

for category in root.iter('Category'):
    category_name = str(category.get('CAT_NAME'))
    category_type = str(category.get('CAT_TYPE'))
    category_gender = str(category.get('CAT_GENDER'))
    category_level = str(category.get('CAT_LEVEL'))
    print(category_name)

    # build a map: participant id -> [given_name, family_name, given_name_partner, family_name_partner, team_name, birthday, nation, club, club_abbr]
    participant_id_to_participant_data_map = {}
    for participant in category.iter('Participant'):
        participant_id = participant.get('PAR_ID')
        if not participant_id:
            continue    # no participant ID found

        participant_id = int(participant_id)  # convert string to int

        pct = participant.find('Person_Couple_Team')
        if pct is None:
            continue    # no Person_Couple_Team entry within Participant found

        pct_type = pct.get('PCT_TYPE')
        if not pct_type:
            continue    # no type found (person/ couple/ team)

        family_name = ''
        given_name = ''
        family_name_partner = ''
        given_name_partner = ''
        team_name = ''
        birthday = ''
        
        if pct_type == 'PER':
            family_name = pct.get('PCT_FNAME')
            given_name = pct.get('PCT_GNAME')
            birthday = pct.get('PCT_BDAY')

            if not family_name:
                family_name = ''
            if not given_name:
                given_name = ''
            if not birthday:
                birthday = ''

            # reverse format for birthdays
            if reverse_birthday_date_format and len(birthday) > 7:
                birthday = birthday[6:8] + '.' + birthday[4:6] + '.' + birthday[0:4]
        elif pct_type == 'COU':
            family_name = str(pct.get('PCT_FNAME'))
            given_name = str(pct.get('PCT_GNAME'))
            family_name_partner = str(pct.get('PCT_PFNAMC'))
            given_name_partner = str(pct.get('PCT_PGNAME'))
            team_name = str(pct.get('PCT_CNAME'))
        elif pct_type == 'PTS':
            team_name = str(pct.get('PCT_CNAME'))
        
        nation = str(pct.get('PCT_NAT'))

        club = pct.find('Club')
        club_name = ''
        club_abbr = ''
        if club is not None:
            club_name = str(club.get('PCT_CNAME'))
            club_abbr = str(club.get('PCT_SNAME'))

        participant_id_to_participant_data_map[participant_id] = [
            given_name,
            family_name,
            given_name_partner,
            family_name_partner,
            team_name,
            birthday,
            nation,
            club_name,
            club_abbr
        ]

    # for all segments within the category
    for segment in category.iter('Segment'):
        segment_name = str(segment.get('SCP_NAME'))
        segment_abbr = str(segment.get('SCP_SNAM'))
        segment_type = str(segment.get('SCP_TYPE'))
        print(segment_name)

        # build a map: skating number -> participant data
        skating_number_to_participant_map = {}
        for performance in segment.iter('Performance'):
            skating_number = performance.get('PRF_STNUM')
            participant_id = performance.get('PAR_ID')
            if skating_number and participant_id:
                # convert strings to integers
                skating_number = int(skating_number)
                participant_id = int(participant_id)
                if participant_id in participant_id_to_participant_data_map:
                    complete_data = participant_id_to_participant_data_map[participant_id]
                    skating_number_to_participant_map[skating_number] = participant_id_to_participant_data_map[participant_id]

        for number, data in sorted(skating_number_to_participant_map.items()):
            output_list_dict.append({
                'Kategorie-Name' : category_name,
                'Kategorie-Typ' : category_type,
                'Kategorie-Geschlecht' : category_gender,
                'Kategorie-Level' : category_level,
                'Segment-Name' : segment_name,
                'Segment-Abk.' : segment_abbr,
                'Segment-Typ' : segment_type,
                'Startnummer' : number,
                'Vorname' : data[0],
                'Name' : data[1],
                'Vorname-Partner' : data[2],
                'Name-Partner' : data[3],
                'Team-Name' : data[4],
                'Geburtstag' : data[5],
                'Nation' : data[6],
                'Club-Name' : data[7],
                'Club-Abk.' : data[8],
            })

# nothing found
if len(output_list_dict) < 1:
    print('No skating order found! Make sure to export the entire event or a category. A segment export contains not enough information.')
    exit(1)


# write data to csv
with open(output_csv_file_path, 'w') as f:
    header = output_list_dict[0].keys()

    csv_writer = csv.DictWriter(f, header)
    csv_writer.writeheader()
    csv_writer.writerows(output_list_dict)
