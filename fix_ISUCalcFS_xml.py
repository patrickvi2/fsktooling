import xml.etree.ElementTree as ET


# defines
fix_participant_club_ids = True
fix_participant_gender = True
fix_person_family_name_capital = False

# input_xml_file_path = 'DEU-Datenassisten-export/toIsuCalcFS.xml'
# output_xml_file_path = 'DEU-Datenassisten-export/out.xml'
input_xml_file_path = '/Users/Brummi/VirtualBox VMs/XChange/OBM20/OBM_from_deu_datenassistent_export.XML'
output_xml_file_path = '/Users/Brummi/VirtualBox VMs/XChange/OBM20/OBM_from_deu_datenassistent_export_fixed2.XML'


# code
tree = ET.parse(input_xml_file_path)
root = tree.getroot()

if fix_participant_club_ids:
    for participant in root.iter('Participant'):
        is_partner = False
        for club in participant.iter('Club'):
            club_id = club.get('PCT_ID')
            if club_id:
                if is_partner:
                    participant.set('PAR_PCLBID', club_id)
                else:
                    participant.set('PAR_CLBID', club_id)
            is_partner = True
                    

if fix_participant_gender:
    for category in root.iter('Category'):
        category_type = category.get('CAT_TYPE')
        category_gender = category.get('CAT_GENDER')
        category_name = category.get('CAT_NAME')

        # change only single skaters (pairs, dance and synchron must be handeled separately)
        if not category_type or category_type != 'S':
            continue

        gender = category_gender
        if 'Herren' in category_name or 'Jungen' in category_name:
            gender = 'M'

        if not gender:
            continue

        for participant in category.iter('Participant'):
            for pct in participant.iter('Person_Couple_Team'):
                pct.set('PCT_GENDER', gender)

if fix_person_family_name_capital:
    def fix_fnamec(elem):
        fnamec = elem.get('PCT_FNAMEC')
        if fnamec:
            elem.set('PCT_FNAMEC', str(fnamec).upper())

    for pct in root.iter('Person_Couple_Team'):
        fix_fnamec(pct)

    for person in root.iter('Person'):
        fix_fnamec(person)

tree.write(output_xml_file_path, encoding='UTF-8')
