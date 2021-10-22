import os, csv
import datetime
import traceback

# settings
input_DEU_participant_csv_file_path = 'OBM22/csv/all/merge.csv'
input_DEU_club_csv_file_path = './DEU/clubs-DEU.csv'
input_DEU_categories_csv_file_path = 'OBM22/csv/deu_categories.csv'
output_athletes_file_path = './OBM22/csv/person.csv'
output_participant_file_path = './OBM22/csv/participants.csv'

deu_type_to_isucalcfs = {'Herren' : 'S', 'Damen' : 'S', 'Einzellauf': 'S', 'Paarlaufen' : 'P', 'Eistanzen' : 'D', 'Synchron': 'T'}
deu_gender_to_isucalcfs = {'Herren' : 'M', 'Damen' : 'F', 'Einzellauf': 'F', 'Paarlaufen' : 'T', 'Eistanzen' : 'T', 'Synchron': 'T'}
deu_level_to_isucalcfs = {'Meisterklasse' : 'S', 'Juniorenklasse' : 'J', 'Jugendklasse' : 'J', 'Nachwuchsklasse' : 'V'}

def convert(input_participants, input_clubs, input_categories, output_athletes_file_path, output_participant_file_path):

    if not os.path.isfile(input_participants) or \
       not os.path.isfile(input_DEU_club_csv_file_path) or \
       not os.path.isfile(input_DEU_categories_csv_file_path):
        print('Not all files found.')
        return 1
    
    # read clubs
    try:
        clubs_file = open(input_clubs, 'r')
        club_reader = csv.DictReader(clubs_file, delimiter=';')

        club_abbr_to_nation = {}

        for club_dict in club_reader:
            club_abbr_to_nation[club_dict['Abk.']] = {'name' : club_dict['Name'], 'nation' : club_dict['Region']}
    except:
        print('Error while parsing clubs.')
    finally:
        clubs_file.close()

    # read categories
    try:
        categories_dict = {}
        cats_file = open(input_categories, 'r')
        cat_reader = csv.DictReader(cats_file)
        for cat_dict in cat_reader:
            cat_name = cat_dict['Wettbewerb/Prüfung']
            cat_deu_type = cat_dict['Disziplin']
            cat_deu_level = cat_dict['Kategorie']
            
            cat_type = deu_type_to_isucalcfs[cat_deu_type] if cat_deu_type in deu_type_to_isucalcfs else ''
            cat_gender = deu_gender_to_isucalcfs[cat_deu_type] if cat_deu_type in deu_gender_to_isucalcfs else ''
            cat_level = deu_level_to_isucalcfs[cat_deu_level] if cat_deu_level in deu_level_to_isucalcfs else ''

            if not cat_type or not cat_gender or not cat_level:
                print('Warning: Unable to convert category following %s|%s|%s' % (cat_name, cat_name, cat_level))
            else:
                categories_dict[cat_name] = {'Kategorie-Name' : cat_name, 'Kategorie-Typ' : cat_type, 'Kategorie-Geschlecht': cat_gender, 'Kategorie-Level': cat_level}
    except:
        print('Error while converting categories.')
    finally:
        cats_file.close()
        

    try:
        pars_file = open(input_participants, 'r')
        par_reader = csv.DictReader(pars_file)
        check_field_names = True


        athlete_list = []
        participant_list = []
        next_is_male_partner = False
        team_set = set() # a set storing (team_id, team_name) to check, if team has been added to the participants already
        couple_dict = {} # safe a list of couple members (storing ID -> par), if partner is found -> create participant and delete from this list
        par_last = None

        for par in par_reader:
            # print(par)

            field_names = ['Wettbewerb/Prüfung', 'Team ID', 'Team Name', 'ID ( ehm. Sportpassnr.)', 'Name', 'Vorname', 'Geb. Datum', 'Vereinskürzel']
            # check if all csv field names exist
            if check_field_names:
                missing_field_name_found = False
                for field_name in field_names:
                    if field_name not in par:
                        print('Error: Invalid participant csv file. Missing column "%s"' % field_name)
                        missing_field_name_found = True
                if missing_field_name_found:
                    break
                check_field_names = False

            par_category = par['Wettbewerb/Prüfung']
            par_team_id = par['Team ID']
            par_team_name = par['Team Name']
            par_id = par['ID ( ehm. Sportpassnr.)']
            par_family_name = par['Name']
            par_first_name = par['Vorname']
            par_bday = datetime.datetime.fromisoformat(par['Geb. Datum']) if par['Geb. Datum'] else None
            par_club_abbr = par['Vereinskürzel']
            par_place_status = par['Platz/Status']

            cat = {}
            if par_category in categories_dict:
                cat = categories_dict[par_category]
            else:
                print('Warning: Cannot find category "%s" for athlete "%s %s". Skipping athlete.' % (par_category, par_first_name, par_family_name))
                continue

            cat_type = cat['Kategorie-Typ']
            cat_gender = cat['Kategorie-Geschlecht']
            cat_level = cat['Kategorie-Level']

            # guess athlete gender
            par_gender = 'F'
            couple_found_id = 0
            if cat_type in ['P', 'D']:
                if par_team_id:
                    par_team_id_trimmed = par_team_id.strip()
                    if par_team_id_trimmed.endswith(str(par_id)): # team id ends with male team id
                        par_gender = 'M'
                    elif par_team_id_trimmed.startswith(str(par_id)):
                        par_gender = 'F'
                    else:
                        print("Error: Unable to add couple. ID cannot be found in team id for following participant: %s" % str(par))
                        continue

                    if par_team_id_trimmed not in couple_dict:
                        couple_dict[par_team_id_trimmed] = {}
                        next_is_male_partner = True
                    else:
                        next_is_male_partner = False
                        couple_found_id = par_team_id_trimmed
                    couple_dict[par_team_id_trimmed][par_gender] = par
                else: # no team id set -> assume: first is female, second is male
                    if next_is_male_partner:
                        par_gender = 'M'
                        next_is_male_partner = False
                    else:
                        next_is_male_partner = True
            else:
                if cat_type != 'T': # single skater -> use category gender
                    par_gender = cat['Kategorie-Geschlecht']
                if next_is_male_partner:
                    print('Error: Skipping athlete. No partner can be found for: %s' % str(par_last))
                next_is_male_partner = False

            if par_club_abbr in club_abbr_to_nation:
                club = club_abbr_to_nation[par_club_abbr]
                par_club = club['name']
                par_nation = club['nation']
            else:
                print('Error: Club not found: "%s". Cannot derive nation for following athlete.')
                print(par)
                print('Skipping athlete.')
                par_last = par
                continue
            
            # add athletes to csv data
            athlete_list.append([par_first_name, par_family_name, par_gender, par_club_abbr, par_nation, par_id, par_bday.strftime('%Y%m%d') if par_bday else ''])

            if cat_type != 'S' and (next_is_male_partner or (par_team_id, par_team_name) in team_set):
                par_last = par
                continue # participant is a couple and cannot be added yet or is a team and already in the team list

            # add participants
            par_dict = cat.copy()
            par_dict['Segment-Name'] = ''
            par_dict['Segment-Abk.'] = ''
            par_dict['Segment-Typ'] = ''
            par_dict['Startnummer'] = ''
            par_dict['Vorname'] = ''
            par_dict['Name'] = ''
            par_dict['Vorname-Partner'] = ''
            par_dict['Name-Partner'] = ''
            par_dict['Team-Name'] = ''
            par_dict['Geburtstag'] = ''
            par_dict['Nation'] = ''
            par_dict['Club-Name'] = ''
            par_dict['Club-Abk.'] = ''
            par_dict['Status'] = par_place_status
            if cat_type == 'S':
                par_dict['Vorname'] = par_first_name
                par_dict['Name'] = par_family_name
                par_dict['Geburtstag'] = par_bday.strftime('%d.%m.%Y')
                par_dict['Nation'] = par_nation
                par_dict['Club-Name'] = par_club
                par_dict['Club-Abk.'] = par_club_abbr
            else: # couple or team
                if cat_type == 'T': # Synchron
                    par_dict['Team-Name'] = par_team_name
                    par_dict['Nation'] = par_nation
                    par_dict['Club-Name'] = par_club
                    par_dict['Club-Abk.'] = par_club_abbr
                    team_set.add((par_team_id, par_team_name))
                else: # couple
                    if couple_found_id:
                        for gender in couple_dict[couple_found_id]:
                            if gender != par_gender:
                                par_last = couple_dict[couple_found_id][gender]
                    par_female_first_name = par_last['Vorname']
                    par_female_family_name = par_last['Name']
                    par_female_club_abbr = par_last['Vereinskürzel']
                    par_female_club = ''
                    if par_female_club_abbr in club_abbr_to_nation:
                        par_female_club = club_abbr_to_nation[par_female_club_abbr]['name']
                        par_female_nation = club_abbr_to_nation[par_female_club_abbr]['nation']

                    par_team_name = '%s %s / %s %s' % (par_female_first_name, par_female_family_name, par_first_name, par_family_name)
                    if par_club_abbr == par_female_club_abbr: # same club
                        par_team_club_name = par_club
                        par_team_club_abbr = par_club_abbr
                    else:
                        par_team_club_name = par_female_club + " / " + par_club
                        par_team_club_abbr = par_female_club_abbr + " / " + par_club_abbr
                    if par_nation == par_female_nation:
                        par_team_nation = par_nation
                    else:
                        par_team_nation = par_female_nation + " / " + par_nation
                    par_dict['Vorname'] = par_female_first_name
                    par_dict['Name'] = par_female_family_name
                    par_dict['Vorname-Partner'] = par_first_name
                    par_dict['Name-Partner'] = par_family_name
                    par_dict['Team-Name'] = par_team_name
                    par_dict['Nation'] = par_team_nation
                    par_dict['Club-Name'] = par_team_club_name
                    par_dict['Club-Abk.'] = par_team_club_abbr

            participant_list.append(par_dict)
                
            par_last = par

        # write files
        # athletes / persons
        if athlete_list:
            with open(output_athletes_file_path, 'w') as f:
                w = csv.writer(f, delimiter='|')
                w.writerows(athlete_list)

        # participants
        if participant_list:
            with open(output_participant_file_path, 'w') as f:
                w = csv.DictWriter(f, participant_list[0].keys())
                w.writeheader()
                w.writerows(participant_list)
        
    except Exception as e:
        print('Error while parsing participants')
        traceback.print_exception()
    finally:
        pars_file.close()

if __name__ == '__main__':
    exit(convert(input_DEU_participant_csv_file_path, input_DEU_club_csv_file_path, input_DEU_categories_csv_file_path, output_athletes_file_path, output_participant_file_path))

