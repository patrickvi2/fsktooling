import csv
import os
from shutil import move

from merge_csv import merge_csv, merge_csv_in_directory
import convert_DEU_meldeformular_to_csv as DEUxlsx
import convert_DEU_meldeformular_csv_to_participant_csv as DEUcsv

csv_path = './OBM22/csv'
obm_path = './OBM22/csv/OBM'
obm_bel_path = obm_path + '_BEL'
obm_gbb_path = obm_path + '_GBB'
gbb_path = './OBM22/csv/GBB'
all_path = './OBM22/csv/all'
all_BEL_path = all_path + '_BEL'

from_LEV_xlsx = False

if from_LEV_xlsx:
    print('Converting XLSX files...')
    DEUxlsx.convert_meldeformular_in_directory(gbb_path, False)
    DEUxlsx.convert_meldeformular_in_directory(obm_path, False)
    DEUxlsx.convert_meldeformular(os.path.join(obm_bel_path,'OBM_BEL.xlsx'), False, True)

    # merge
    print('Merging csv files...')
    print('GBB...')
    merge_csv_in_directory(gbb_path, 'deu_athletes.csv')
    print('OBM...')
    merge_csv_in_directory(obm_path, 'deu_athletes.csv')

    # copy
    move(os.path.join(gbb_path, 'deu_athletes.csv'), os.path.join(all_path,'deu_athletes_GBB.csv'))
    move(os.path.join(obm_path, 'deu_athletes.csv'), os.path.join(all_path,'deu_athletes_OBM.csv'))

    # merge
    print('Merging csv files...')
    print('all...')
    merge_csv_in_directory(all_path, 'deu_athletes.csv')

    print('Merging csv files...')
    print('all including BEL athletes...')
    merge_csv([os.path.join(all_path, 'deu_athletes_OBM.csv'), os.path.join(obm_bel_path, 'OBM_BEL_deu_athletes.csv')],
            os.path.join(all_path, 'deu_athletes_OBM_all.csv'), log_file_path='log_merge_csv_BEL.txt')

    # converting
    print('Converting deu_athletes to persons and participants...')
    DEUcsv.convert('./OBM22/csv/all/deu_athletes.csv', './OBM22/csv/clubs-DEU.csv', './OBM22/csv/deu_categories.csv', 
                './OBM22/csv/person.csv', './OBM22/csv/participants_national.csv')

    merge_csv([os.path.join(csv_path, 'participants_national.csv'),
            os.path.join(csv_path, 'participants_international.csv')],
            os.path.join(csv_path, 'participants.csv'))

else:
    DEUxlsx.convert_meldeformular_in_directory(obm_gbb_path, False)

    merge_csv_in_directory(obm_gbb_path, 'deu_athletes.csv')

    # converting
    print('Converting deu_athletes to persons and participants...')
    DEUcsv.convert('./OBM22/csv/OBM_GBB/deu_athletes.csv', './OBM22/csv/clubs-DEU.csv', './OBM22/csv/deu_categories_groups.csv', 
                './OBM22/csv/person.csv', './OBM22/csv/participants_national.csv')

    merge_csv([os.path.join(csv_path, 'participants_national.csv'),
            os.path.join(csv_path, 'participants_international.csv')],
            os.path.join(csv_path, 'participants.csv'), 
            log_file_path=os.path.join(csv_path, 'log_merge_csv.txt'))
