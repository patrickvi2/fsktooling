from unicodedata import category
import mysql.connector
import io

from output import ParticipantCsvOutput
import model

cat_type_to_class = {
    0: 'men',
    1: 'women',
    2: 'pairs',
    3: 'icedance',
    4: 'synchron',
}


seg_type_to_FSM_file_name_prefix = {
    0: 'QUAL',
    1: 'FNL-',
    2: 'QUAL'
}

con = mysql.connector.connect(user='sa', password='FSManager1.6', host='192.168.178.87', database='test')
# con = mysql.connector.connect(user='sa', password='fsmanager', host='127.0.0.1', database='test')

cursor = con.cursor()


def get_date(datetime) -> str:
    return datetime.strftime("%d.%m.%Y")


def get_file_name(cat_name : str, cat_type : int, cat_level : int, file_name : str, seg_name = '', seg_type = 0, seg_type_num = 0):
    cat_type_to_FSM_file_name_prefix = {
        0: 'FSKMSINGLES',
        1: 'FSKMSINGLES',
        2: 'FSKXPAIRS',
        3: 'FSKXICEDANCE',
        4: 'FSKXSYNCHRON'
    }
    cat_level_to_FSM_file_name_prefix = {
        0: '',
        1: 'JUNIOR',
        2: 'BASENOVICE',
        3: 'ADVANOVICE',
        4: 'INTENOVICE',
        5: 'ADULT',
        6: 'MIXEDAGE'
    }

    path = cat_name + '/'
    prefix1 = cat_type_to_FSM_file_name_prefix[cat_type]
    prefix1 += (12 - len(prefix1)) * '-'
    prefix2 = cat_level_to_FSM_file_name_prefix[cat_level]
    prefix2 += (10 - len(prefix2)) * '-'
    prefix3 = ''
    if seg_name:
        path += seg_name + '/'
        prefix3 = seg_type_to_FSM_file_name_prefix[seg_type] + "%06d" % (100 * seg_type_num)
    prefix3 += (12 - len(prefix3)) * '-'

    path += prefix1 + prefix2 + prefix3 + '_' + file_name + '.pdf'
    return path

csv = ParticipantCsvOutput('FSMTest/starting_order.csv')

# categories and segemtens
cursor.execute("SELECT Id, Name, Level, Type FROM category")
for (cat_id, cat_name, cat_level, cat_type) in list(cursor):
    cursor.execute("SELECT Id, Name, ShortName, SegmentType FROM segment WHERE Category_Id = " + str(cat_id))
    print(cat_name)
    # TODO: category gender
    cat = model.Category(cat_name, model.CategoryType.from_value(cat_type, model.DataSource.FSM), model.CategoryLevel.from_value(cat_level, model.DataSource.FSM), model.Gender.FEMALE)

    for (seg_id, seg_name, seg_short_name, seg_type) in list(cursor):
        print(seg_name)
        seg = model.Segment(seg_name, seg_short_name, model.SegmentType.from_value(seg_type, model.DataSource.FSM))
        if cat_type in [0, 1]: # singles
            cursor.execute("SELECT person.FederationId, person.FirstName, person.LastName, person.BirthDate, person.Gender, person.Nation_Id, club.Name, person.Club, competitorresult.StartNumber "
                           "FROM competitorresult "
                           "    JOIN entry ON competitorresult.Entry_Id = entry.Id "
                           "    JOIN single ON entry.Competitor_Id = single.Competitor_Id_Pk "
                           "    JOIN person ON person.Id = single.Person_Id "
                           "    JOIN club ON club.ShortName = person.Club "
                          f"WHERE competitorresult.Segment_Id = {str(seg_id)} "
                           "ORDER BY competitorresult.StartNumber ASC")
            for (id, first_name, last_name, bday, gender, nation, club_name, club_abbr, start_number) in cursor:
                club = model.Club(club_name, club_abbr, nation)
                person = model.Person(id, last_name, first_name, model.Gender.from_value(gender, model.DataSource.FSM), bday, club)
                participant = model.ParticipantSingle(person, cat)
                csv.add_participant_with_segment_start_number(participant, seg, start_number)

        elif cat_type in [2, 3]: # pairs
            cursor.execute("SELECT partner1.FirstName, partner1.LastName, partner2.FirstName, partner2.LastName, competitorresult.StartNumber "
                           "FROM competitorresult "
                           "    JOIN entry ON competitorresult.Entry_Id = entry.Id "
                           "    JOIN couple ON entry.Competitor_Id = couple.Competitor_Id_Pk "
                           "    JOIN person AS partner1 ON partner1.Id = couple.PersonLady_Id "
                           "    JOIN person AS partner2 ON partner2.Id = couple.PersonMale_Id "
                           "WHERE competitorresult.Segment_Id = " + str(seg_id))
        elif cat_type == 4:
            cursor.execute(
                "SELECT synchronizedteam.Name, competitorresult.StartNumber "
                "FROM competitorresult "
                "    JOIN entry ON competitorresult.Entry_Id = entry.Id "
                "    JOIN synchronizedteam ON entry.Competitor_Id = synchronizedteam.Competitor_Id_Pk "
                "WHERE competitorresult.Segment_Id = " + str(seg_id))
        for x in cursor:
            print(x)

csv.write_file()

# close database connection
con.close()
