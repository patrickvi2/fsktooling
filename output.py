import csv
import xml.etree.ElementTree as ET
from datetime import datetime

import model

# virtual output base class - responsible for gathering infos and writing files
class OutputBase:
    def __init__(self, file_path: str) -> None:
        self.path = file_path
    def add_person(self):
        raise NotImplementedError()
    def add_participant(self):
        raise NotImplementedError()
    def write_file(self):
        raise NotImplementedError()

# athletes / persons
class PersonCsvOutput(OutputBase):
    def __init__(self, file_path: str):
        super().__init__(file_path)
        self.persons = list()

    def add_participant(self, participant: model.ParticipantBase):
        pass

    def add_person(self, person: model.Person):
        bday = person.bday.strftime('%Y%m%d') if person.bday else ''
        self.persons.append([person.first_name, person.family_name, person.gender.CALC(), person.club.abbr, person.club.nation, person.id, bday])

    def write_file(self):
        if self.persons:
            with open(self.path, 'w') as f:
                w = csv.writer(f, delimiter='|')
                w.writerows(self.persons)


# participants
class ParticipantCsvOutput(OutputBase):
    def __init__(self, file_path: str) -> None:
        super().__init__(file_path)
        self.participant_csv_data = []

    @staticmethod
    # def get_participant_dict(participant: model.ParticipantBase, segment: Union[model.Segment, None], start_number: Union[int, None]):
    def get_participant_dict(participant: model.ParticipantBase, segment = None, start_number = None):
        output = {
                    'Kategorie-Name' : participant.cat.name,
                    'Kategorie-Typ' : participant.cat.type.CALC(),
                    'Kategorie-Geschlecht' : participant.cat.gender.CALC(),
                    'Kategorie-Level' : participant.cat.level.CALC(),
                    'Segment-Name' : None,
                    'Segment-Abk.' : None,
                    'Segment-Typ' : None,
                    'Startnummer' : start_number,
                    'Id' : None,
                    'Vorname' : None,
                    'Name' : None,
                    'Id-Partner' : None,
                    'Vorname-Partner' : None,
                    'Name-Partner' : None,
                    'Team-Name' : None,
                    'Geburtstag' : None,
                    'Nation' : None,
                    'Club-Name' : None,
                    'Club-Abk.' : None,
                }

        if segment:
            output['Segment-Name'] = segment.name
            output['Segment-Abk.'] = segment.abbr
            output['Segment-Typ'] = segment.type.CALC()
        
        if start_number:
            output['Startnummer'] = start_number

        if(type(participant) is model.ParticipantSingle):
            output['Id'] = participant.person.id
            output['Vorname'] = participant.person.first_name
            output['Name'] = participant.person.family_name
            output['Geburtstag'] = participant.person.bday.strftime('%d.%m.%Y')
            output['Nation'] = participant.person.club.nation
            output['Club-Name'] = participant.person.club.name
            output['Club-Abk.'] = participant.person.club.abbr
        elif(type(participant) is model.ParticipantCouple):
            p1 = participant.couple.partner_1
            p2 = participant.couple.partner_2
            output['Id'] = participant.couple.partner_1.id
            output['Vorname'] = p1.first_name
            output['Name'] = p1.family_name
            output['Id-Partner'] = p2.id
            output['Vorname-Partner'] = p2.first_name
            output['Name-Partner'] = p2.family_name
            par_team_name = '%s %s / %s %s' % (
                p1.first_name, 
                p1.family_name, 
                p2.first_name, 
                p2.family_name)
            output['Team-Name'] = par_team_name

            if p1.club.abbr == p2.club.abbr: # same club
                par_team_club_name = p1.club.name
                par_team_club_abbr = p1.club.abbr
            else:
                par_team_club_name = p1.club.name + " / " + p2.club.name
                par_team_club_abbr = p1.club.abbr + " / " + p2.club.abbr
            output['Club-Name'] = par_team_club_name
            output['Club-Abk.'] = par_team_club_abbr

            if p1.club.nation == p2.club.nation:
                par_team_nation = p1.club.nation
            else:
                par_team_nation = p1.club.nation + " / " + p2.club.nation
            output['Nation'] = par_team_nation
        elif(type(participant) is model.ParticipantTeam):
            output['Team-Name'] = participant.team.name
            output['Nation'] = participant.team.club.nation
            output['Club-Name'] = participant.team.club.name
            output['Club-Abk.'] = participant.team.club.abbr
        else:
            print('Error: unknown participant type')

        return output

    def add_participant(self, participant: model.ParticipantBase):
        self.participant_csv_data.append(self.get_participant_dict(participant))

    def add_participant_with_segment_start_number(self, participant: model.ParticipantBase, segment: model.Segment, start_number: int):
        self.participant_csv_data.append(self.get_participant_dict(participant, segment, start_number))

    def add_person(self, person: model.Person):
        pass

    def write_file(self):
        if 0 == len(self.participant_csv_data):  # no participants
            print("No participants to write to CSV.")
            return
        # write data to csv
        with open(self.path, 'w') as f:
            header = self.participant_csv_data[0].keys()
            csv_writer = csv.DictWriter(f, header)
            csv_writer.writeheader()
            csv_writer.writerows(self.participant_csv_data)


class OdfParticOutput(OutputBase):
    def __init__(self, file_path: str) -> None:
        super().__init__(file_path)
        self.competition_elem = ET.Element("Competition")
        self.disciplin = "FSK" + 31 * "-"
        self.accreditation_id = 1
    
    def add_participant(self, participant: model.ParticipantBase):
        category = participant.cat

        # skip adding persons to a category / segment, if it is not a ISU category
        if not category.level.is_ISU_category():
            return

        persons = []
        if type(participant) == model.ParticipantSingle:
            persons.append(participant.person)
        # TODO add couples and teams to DT_PARTIC_TEAM.xml
        # if type(participant) == model.ParticipantCouple:
        #     persons.append(participant.couple.partner_1)
        #     persons.append(participant.couple.partner_2)
        # if type(participant) == model.ParticipantTeam:
        #     for person in participant.team.persons:
        #         persons.append(person)
        for person in persons:
            dis_elem = self.competition_elem.find(f"./Participant/Discipline[@IFId='{person.id}']")
            event_elem = ET.SubElement(dis_elem, "RegisteredEvent", {"Event" : self.get_discipline_code(category)})
            event_club_attrib = {
                "Type" : "ER_EXTENDED",
                "Code" : "CLUB"
            }
            ET.SubElement(event_elem, "EventEntry", {**event_club_attrib, **{"Pos" : "1", "Value" : person.club.name}})
            ET.SubElement(event_elem, "EventEntry", {**event_club_attrib, **{"Pos" : "2", "Value" : person.club.abbr}})
        pass

    def add_person(self, person: model.Person):
        first = person.first_name
        last = person.family_name
        participant_attrib = {
            "Code" : str(self.accreditation_id),
            "Parent" : str(self.accreditation_id),
            "Status" : "ACTIVE",
            "GivenName" : first,
            "FamilyName" : last,
            "PrintName" : f"{first} {last.upper()}",
            "PrintInitialName" : f"{first[0]} {last.upper()}",
            "TVName" : f"{first} {last.upper()}",
            "TVInitialName" : f"{first[0]}. {last.upper()}",
            "Gender" : person.gender.CALC(),
            "Organisation" : person.club.nation,
            "BirthDate" : person.bday.strftime('%Y-%m-%d'),
            "Height" : "-",
            "MainFunctionId" : "AA01", # AA01 - accreditated athlete - comes from Olympia
            "Current" : "true",
            "ModificationIndicator" : "N"
            }
        par_elem = ET.SubElement(self.competition_elem, "Participant", attrib=participant_attrib)
        ET.SubElement(par_elem, "Discipline", {"Code" : self.disciplin, "IFId" : person.id})

        self.accreditation_id += 1

    def write_file(self):
        if len(self.competition_elem) > 0:
            now = datetime.now()
            date = now.strftime("%Y-%m-%d")
            competition_attrib = {
                "CompetitionCode" : "TestName",
                "DocumentCode" : self.disciplin,
                "DocumentType" : "DT_PARTIC_UPDATE",
                "Version" : "1",
                "FeedFlag" : "P",
                "Date" : date,
                "Time" : "123456789",
                "LogicalDate" : date,
                "Source" : "FSKFSK1"
            }
            root = ET.Element("OdfBody", competition_attrib)
            root.insert(0, self.competition_elem)
            ET.ElementTree(root).write(self.path, encoding="utf-8", xml_declaration=True)
        else:
            print("OdfParticOutput: No persons found for writing. Skip creating file.")

    @staticmethod
    def get_discipline_code(category: model.Category):

        code = "FSK" + category.gender.ODF() + category.type.ODF()
        code += "-" * (12 - len(code))
        code += category.level.ODF()

        # add trailing dashes (discipline code always consists of 34 characters)
        code += "-" * (34 - len(code))
        return code