from datetime import date
import xml.etree.ElementTree as ET

from fsklib import model
from fsklib.output import ParticipantCsvOutput

# settings / defines
isucalcfs_xml_file_path = "BJM22/xml/BJM22-011.XML"
output_csv_file_path = "BJM22Test/starting_order.csv"

# script code
tree = ET.parse(isucalcfs_xml_file_path)

root = tree.getroot()

# output_list_dict = []
csv = ParticipantCsvOutput(output_csv_file_path)

data_src = model.DataSource.CALC
for category in root.iter('Category'):
    category_name = str(category.get('CAT_NAME'))
    category_type = str(category.get('CAT_TYPE'))
    category_gender = str(category.get('CAT_GENDER'))
    category_level = str(category.get('CAT_LEVEL'))
    cat = model.Category(category_name, model.CategoryType.from_value(category_type, data_src), model.CategoryLevel.from_value(category_level, data_src), model.Gender.from_value(category_gender, data_src))
    print(category_name)

    # build a map: participant id -> participant
    participant_id_to_participant_data_map = {}
    for participant_xml in category.iter('Participant'):
        participant_id = participant_xml.get('PAR_ID')
        if not participant_id:
            print("No participant found for %s" % str(participant_xml))
            continue    # no participant ID found

        participant_id = int(participant_id)  # convert string to int

        pct = participant_xml.find('Person_Couple_Team')
        if pct is None:
            continue    # no Person_Couple_Team entry within Participant found

        pct_type = pct.get('PCT_TYPE')
        if not pct_type:
            continue    # no type found (person/ couple/ team)

        nation = str(pct.get('PCT_NAT'))
        club_xml = pct.find('Club')

        if club_xml is None:
            continue

        club_name = str(club_xml.get('PCT_CNAME'))
        club_abbr = str(club_xml.get('PCT_SNAME'))
        club = model.Club(club_name, club_abbr, nation)

        participant = None


        def get_person(xml_element, club: model.Club):
            family_name = xml_element.get('PCT_FNAME')
            given_name = xml_element.get('PCT_GNAME')
            birthday = xml_element.get('PCT_BDAY')
            gender = xml_element.get('PCT_GENDER')
            participant_federation_id = xml_element.get('PCT_EXTDT')

            bday = None
            if birthday:
                bday = date(int(birthday[0:4]), int(birthday[4:6]), int(birthday[6:8]))

            if not family_name:
                family_name = ''
            if not given_name:
                given_name = ''
            if not birthday:
                birthday = ''

            return model.Person(participant_federation_id, family_name, given_name, model.Gender.from_value(gender, model.DataSource.CALC), bday, club)
        

        if pct_type == 'PER':
            person = get_person(pct, club)
            participant = model.ParticipantSingle(person, cat)
        elif pct_type == 'COU':
            partners = []
            for person_xml in pct.findall('Team_Members/Person'):
                partners.append(get_person(person_xml, club))

            if len(partners) < 2:
                continue
            couple = model.Couple(partners[0], partners[1])
            participant = model.ParticipantCouple(couple, cat)
        elif pct_type == 'PTS':
            team_name = str(pct.get('PCT_CNAME'))
            team = model.Team(participant_id, team_name, club, [])
            participant = model.ParticipantTeam(team, cat)

        if participant:
            participant_id_to_participant_data_map[participant_id] = participant

    # for all segments within the category
    for segment_xml in category.iter('Segment'):
        segment_name = str(segment_xml.get('SCP_NAME'))
        segment_abbr = str(segment_xml.get('SCP_SNAM'))
        segment_type = str(segment_xml.get('SCP_TYPE'))
        print(segment_name)
        segment = model.Segment(segment_name, segment_abbr, model.SegmentType.from_value(segment_type, model.DataSource.CALC))

        # build a map: skating number -> participant data
        skating_number_to_participant_map = {}
        for performance in segment_xml.iter('Performance'):
            skating_number = performance.get('PRF_STNUM')
            participant_id = performance.get('PAR_ID')
            if skating_number and participant_id:
                # convert strings to integers
                skating_number = int(skating_number)
                participant_id = int(participant_id)
                if participant_id in participant_id_to_participant_data_map:
                    skating_number_to_participant_map[skating_number] = participant_id_to_participant_data_map[participant_id]

        for number, data in sorted(skating_number_to_participant_map.items()):
            csv.add_participant_with_segment_start_number(data, segment, number)

# nothing found
if len(csv.participant_csv_data) < 1:
    print('No skating order found! Make sure to export the entire event or a category. A segment export contains not enough information.')
    exit(1)


# write data to csv
csv.write_file()
