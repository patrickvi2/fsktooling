import os, shutil
import csv
import unicodedata

# defines
input_csv_file_path = './OBM22/csv/participants.csv'
input_music_dir = '/Volumes/BEV/Musiken/2 - Name korrigiert'
output_music_root_dir = '/Volumes/BEV/Musiken/3 - sortiert'

should_create_directory_structure = True
should_copy_music_files = False
should_add_skating_number_to_file_name = True
should_create_m3u_playlist = True # one playlist per category and segment

# code

input_music_file_names_with_ext = os.listdir(input_music_dir)

input_music_file_names = []
input_music_file_exts = []
for music_file_name in input_music_file_names_with_ext:
    music_file_name = unicodedata.normalize('NFC', unicodedata.normalize('NFD', music_file_name))
    name, ext = os.path.splitext(music_file_name)
    input_music_file_names.append(name)
    input_music_file_exts.append(ext)

categories = {}
participants = []

count_found = 0
count_missing = 0
count_ambiguous = 0

files_found = set()

with open(input_csv_file_path, 'r') as f:
    csv_list_dict = csv.DictReader(f)
    
    # copy csv data to participant list
    # build category and segment structure (as nested dictionaries)
    for entry in csv_list_dict:
        participants.append(entry)
        cat_name = entry['Kategorie-Name']
        if cat_name in categories:
            categories[cat_name]['segments'][entry['Segment-Abk.']] = {'name' : entry['Segment-Name'], 'type' : entry['Segment-Typ']}
        else:
            categories[cat_name] = {
                                        'type' : entry['Kategorie-Typ'],
                                        'gender' : entry['Kategorie-Geschlecht'],
                                        'level' : entry['Kategorie-Level'],
                                        'segments' : {
                                            entry['Segment-Abk.'] : {
                                                'name' : entry['Segment-Name'], 'type' : entry['Segment-Typ']
                                            }
                                        }
                                    }

print(categories)

# create folder structure
if should_create_directory_structure:
    for cat_name, cat_data in categories.items():
        category_dir = os.path.join(output_music_root_dir, cat_name)
        if not os.path.isdir(category_dir):
            os.mkdir(category_dir)

        for seg in cat_data['segments']:
            segment_dir = os.path.join(category_dir, seg)
            if not os.path.isdir(segment_dir):
                os.mkdir(segment_dir)

def normalize_string(s : str):
    # remove spaces, dashes, dots, commas and underscores in file names
    translation_table = str.maketrans('','',' -_.,')

    return s.translate(translation_table).casefold().replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue')

truncated_music_file_names = [normalize_string(s) for s in input_music_file_names]

cat_name_old = ''
seg_name_old = ''
playlist_dict = {}
for participant in participants:
    cat_name = participant['Kategorie-Name']
    cat_type = participant['Kategorie-Typ']
    cat_gender = participant['Kategorie-Geschlecht']
    cat_level = participant['Kategorie-Level']
    segment_name = participant['Segment-Name']
    segment_type = participant['Segment-Typ']
    segment_abbr = participant['Segment-Abk.']
    skating_number = participant['Startnummer']

    # copy no music for pattern dances
    if segment_type == 'D':
        continue

    if cat_name_old != cat_name:
        print('# ' + cat_name)
        cat_name_old = cat_name
    
    if seg_name_old != segment_name:
        print('## ' + segment_name)
        seg_name_old = segment_name

        if playlist_dict:
            playlist_path = os.path.join(playlist_dict['dir'], '0 - Playlist.m3u')
            with open(playlist_path, 'w') as pf:
                pf.writelines('%s\n' % n for i, n in sorted(playlist_dict['names'].items()))

            playlist_dict = {}

    find_name = False
    find_name_partner = False
    find_team_name = False
    find_birthday = False

    if cat_type == 'S':
        find_name = True
        find_birthday = True
    elif cat_type == 'P' or cat_type == 'D':
        find_name = True
        find_name_partner = True
    elif cat_type == 'T':
        find_team_name = True

    def find_indices_for_matching_search_string(string_list : list, search_string : str) -> set:
        indices = set()
        if not search_string:
            return indices
        search_string = normalize_string(search_string)
        for i, s in enumerate(string_list):
            if search_string in s:
                indices.add(i)

        return indices

    def find_indices_for_full_name(string_list : list, given_name : str, family_name : str) -> set:
        name = given_name + family_name
        valid_idx_set = find_indices_for_matching_search_string(truncated_music_file_names, name)

        name = family_name + given_name
        valid_idx_set =  valid_idx_set.union(find_indices_for_matching_search_string(string_list, name))

        if not valid_idx_set:
            valid_idx_set = find_indices_for_matching_search_string(string_list, family_name)
        
        return valid_idx_set


    valid_music_nums_name = set()
    if find_name:
        family_name = participant['Name']
        given_name = participant['Vorname']
        valid_music_nums_name = find_indices_for_full_name(truncated_music_file_names, given_name, family_name)

    valid_music_nums_name_partner = set()
    if find_name_partner:
        family_name = participant['Name-Partner']
        given_name = participant['Vorname-Partner']
        valid_music_nums_name_partner = find_indices_for_full_name(truncated_music_file_names, given_name, family_name)

    valid_music_nums_name_team = set()
    if find_team_name:
        team_name = participant['Team-Name']
        valid_music_nums_name_team = find_indices_for_matching_search_string(truncated_music_file_names, team_name)

    valid_music_nums_bday = set()
    if find_birthday:
        bday = participant['Geburtstag']
        valid_music_nums_bday = find_indices_for_matching_search_string(truncated_music_file_names, bday)
        # bday = bday.replace('.','')
        # valid_music_nums_bday = valid_music_nums_bday.union(find_indices_for_matching_search_string(truncated_music_file_names, bday))


    valid_music_nums = valid_music_nums_name.union(valid_music_nums_name_partner.union(valid_music_nums_name_team.union(valid_music_nums_bday)))
    # find segment
    valid_music_nums_segment = set()
    for valid_music_num in valid_music_nums:
        music_name = input_music_file_names[valid_music_num].upper()

        seg = str(participant['Segment-Abk.']).upper()

        if music_name.endswith(seg):
            valid_music_nums_segment.add(valid_music_num)
        else:
            if cat_type == 'D': # dance
                if segment_type == 'S': # short
                    segs = ['RD', 'RT', 'OD']
                elif segment_type == 'F': # free
                    segs = ['FD', 'KT']
            else: # single, pairs and synchron
                if segment_type == 'S': # short
                    segs = ['SP', 'KP']
                elif segment_type == 'F': # free
                    segs = ['FS', 'KR', 'Kür', 'FP']
            
            for seg in segs:
                if music_name.endswith(seg):
                    valid_music_nums_segment.add(valid_music_num)
                    break
    # still ambiguous -> try to solve with intersections
    if len(valid_music_nums_segment) > 1:
        valid_music_nums = set()
        if find_name and valid_music_nums_name:
            valid_music_nums = valid_music_nums_name
        if find_name_partner and valid_music_nums_name_partner:
            if valid_music_nums:
                valid_music_nums = valid_music_nums.intersection(valid_music_nums_name_partner)
            else:
                valid_music_nums = valid_music_nums_name_partner
        if find_birthday and valid_music_nums_bday:
            if valid_music_nums:
                valid_music_nums = valid_music_nums.intersection(valid_music_nums_bday)
            else:
                valid_music_nums = valid_music_nums_bday
        if find_team_name:
            if valid_music_nums:
                valid_music_nums = valid_music_nums.intersection(valid_music_nums_name_team)
            else:
                valid_music_nums = valid_music_nums_name_team
        valid_music_nums = valid_music_nums.intersection(valid_music_nums_segment)
    else:
        valid_music_nums = valid_music_nums_segment

    valid_music_count = len(valid_music_nums)

    valid_index = None
    if valid_music_count < 1:
        music_log_string = '\033[31m## missing ##\033[0m'
        count_missing += 1
    elif valid_music_count > 1:
        music_log_string = '\033[35m## ambiguous ##\033[0m ('
        for valid_music_num in valid_music_nums:
            music_log_string += input_music_file_names_with_ext[valid_music_num] + ','
            files_found.add(input_music_file_names_with_ext[valid_music_num])
        music_log_string += ')'
        count_ambiguous += 1
    else:
        # music found
        valid_index = valid_music_nums.pop() # there is only one element
        music_log_string = '(\033[32m## found ##\033[0m ' + input_music_file_names_with_ext[valid_index] + ')'
        count_found += 1
        files_found.add(input_music_file_names_with_ext[valid_index])

    name = participant['Name'] + ', ' + participant['Vorname']
    # use team name for couples or teams
    if cat_type != 'S':
        name = participant['Team-Name']
    print('  ' + (str(skating_number) + ' - ') if skating_number else '' + name + ' ' + music_log_string)

    if valid_index is None:
        continue

    input_music_file_name = input_music_file_names_with_ext[valid_index]
    input_music_file_path = os.path.join(input_music_dir, input_music_file_name)

    # add skating number
    if should_add_skating_number_to_file_name:
        output_music_file_name = str(skating_number) + ' - '
    output_music_file_name += input_music_file_name

    output_music_file_dir =os.path.join(output_music_root_dir, cat_name, segment_abbr)
    output_music_file_path = os.path.join(output_music_file_dir, output_music_file_name)
    
    # copy music file
    if should_copy_music_files:
        shutil.copy(input_music_file_path, output_music_file_path)

    if should_create_m3u_playlist and skating_number:
        n = int(skating_number)
        if playlist_dict:
            playlist_dict['names'][n] = output_music_file_name
        else:
            playlist_dict = {'dir' : output_music_file_dir,
                             'names' : {n : output_music_file_name}
                             }

# print statistical data
print('###########')
print('Statistics:')
print('Found: ' + str(count_found) + '(' + str(len(participants)) + ')')
print('Missing: ' + str(count_missing) + '(' + str(len(participants)) + ')')
print('Ambiguous: ' + str(count_ambiguous) + '(' + str(len(participants)) + ')')
print('Files: ' + str(len(input_music_file_names_with_ext)))
print('Unused files:')
for input_file_name in input_music_file_names_with_ext:
    if input_file_name not in files_found:
        print(input_file_name)