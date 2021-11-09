# extract all athletes from a ISUCalcFS event xml
# correct gender for male categories, if possible
# 
# *** intended workflow ***
# fill DEU Meldeformular
# check DEU Meldeformular with http://deu-info.de/datenassistent/excel-validieren
# download generated ISUCalcFS event xml
# extract all athletes from ISUCalcFS export from DEU datenassistent

import xml.etree.ElementTree as ET


# defines
input_xml_file_path = './toIsuCalcFS.xml'
output_xml_file_path = './athletes.xml'


# code
tree = ET.parse(input_xml_file_path)
root = tree.getroot()

output_root = ET.Element('ISUCalcFS')
athlete_list = ET.SubElement(output_root, 'Athlete_List')

for category in root.iter('Category'):
    category_type = category.get('CAT_TYPE')
    category_gender = category.get('CAT_GENDER')
    category_name = category.get('CAT_NAME')

    # change only single skaters (pairs, dance and synchron must be handeled separately)
    gender = None
    if category_type and category_type == 'S':

        gender = category_gender
        if 'Herren' in category_name or 'Jungen' in category_name:
            gender = 'M'

    for participant in category.iter('Participant'):
        # for single participants
        for pct in participant.iter('Person_Couple_Team'):
             # make sure it is a single skater
            typ = pct.get('PCT_TYPE')
            if typ != 'PER':
                continue
            
            if gender:
                pct.set('PCT_GENDER', gender)

            pct.tag = 'Person' # rename xml tag

            athlete_list.append(pct)

        # for couples/ teams -> list of 'Person' elements within xml element 'Team_Members'
        for person in participant.iter('Person'):
            if gender:
                pct.set('PCT_GENDER', gender)

            athlete_list.append(person)

num_athletes = len(athlete_list.getchildren())
print('Found %d athletes' % (num_athletes))

# print(ET.tostring(output_root))
output_tree = ET.ElementTree(output_root)
output_tree.write(output_xml_file_path, encoding='UTF-8')
