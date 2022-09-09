import csv
from datetime import date, datetime
import pathlib
import xml.etree.ElementTree as ET
from xml.dom import minidom

from . import model


# virtual output base class - responsible for gathering infos and writing files
class OutputBase:
    def __init__(self, file_path: pathlib.Path) -> None:
        self.path = file_path
    def add_event_info(self, competition_info: model.Competition) -> None:
        raise NotImplementedError()
    def add_person(self, model: model.Person) -> None:
        raise NotImplementedError()
    def add_participant(self, participant: model.ParticipantBase) -> None:
        raise NotImplementedError()
    def write_file(self) -> None:
        raise NotImplementedError()

# athletes / persons
class PersonCsvOutput(OutputBase):
    def __init__(self, file_path: pathlib.Path):
        super().__init__(file_path)
        self.persons = list()

    def add_event_info(self, competition_info: model.Competition) -> None:
        pass

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
    def __init__(self, file_path: pathlib.Path) -> None:
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

    def add_event_info(self, competition_info: model.Competition) -> None:
        pass

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
    def __init__(self, dir_path: pathlib.Path) -> None:
        super().__init__(dir_path)
        self.competition_elem = ET.Element("Competition")
        self.competition_elem_couples = ET.Element("Competition")
        self.disciplin = "FSK" + 31 * "-"
        self.accreditation_id = 1
        self.competition = None

    def add_event_info(self, competiton_info: model.Competition) -> None:
        self.competition = competiton_info

    def add_participant(self, participant: model.ParticipantBase) -> None:
        category = participant.cat

        persons = []
        if type(participant) == model.ParticipantSingle:
            persons.append(participant.person)
        # TODO add couples and teams to DT_PARTIC_TEAM.xml
        if type(participant) == model.ParticipantCouple:
            persons.append(participant.couple.partner_1)
            persons.append(participant.couple.partner_2)
        # if type(participant) == model.ParticipantTeam:
        #     for person in participant.team.persons:
        #         persons.append(person)
        accreditation_ids = []
        for person in persons:
            par_elem = self.competition_elem.find(f"./Participant/Discipline[@IFId='{person.id}']/..")
            dis_elem = par_elem.getchildren()[0] # there is always only one child -> Discipline
            event_elem = ET.SubElement(dis_elem, "RegisteredEvent", {"Event" : self.get_discipline_code(category)})
            event_club_attrib = {
                "Type" : "ER_EXTENDED",
                "Code" : "CLUB"
            }
            ET.SubElement(event_elem, "EventEntry", {**event_club_attrib, **{"Pos" : "1", "Value" : person.club.name}})
            ET.SubElement(event_elem, "EventEntry", {**event_club_attrib, **{"Pos" : "2", "Value" : person.club.abbr}})
            accreditation_ids.append(par_elem.get('Code'))

        if type(participant) == model.ParticipantCouple:
            first1 = participant.couple.partner_1.first_name
            l = str('test').split()
            initials1 = ''.join([s[0] for s in first1.split()])
            last1 = participant.couple.partner_1.family_name.upper()
            first2 = participant.couple.partner_2.first_name
            initials2 = ''.join([s[0] for s in first2.split()])
            last2 = participant.couple.partner_2.family_name.upper()
            nation = participant.couple.partner_1.club.nation
            if participant.couple.partner_1.club.nation != participant.couple.partner_2.club.nation:
                nation += "/" + participant.couple.partner_2.club.nation

            team_attrib = {
                "Code" : str(self.accreditation_id),
                "Organisation" : nation,
                "Number" : "1",
                "Name" : f"{first1} {last1} / {first2} {last2}",
                "ShortName" : f"{initials1} {last1} / {initials2} {last2}",
                "TeamType" : "CPLW",
                "TVTeamName" : f"{last1}/{last2}",
                "Gender" : "X",
                "Current" : "true",
                "ModificationIndicator" : "N"
                }

            team_elem = ET.SubElement(self.competition_elem_couples, "Team", team_attrib)
            comp_elem = ET.SubElement(team_elem, "Composition")
            for count, id in enumerate(accreditation_ids, 1):
                ET.SubElement(comp_elem, "Athlete", {"Code" : id, "Order": str(count)})

            team_id = f"{participant.couple.partner_1.id}-{participant.couple.partner_2.id}"

            dis_elem = ET.SubElement(team_elem, "Discipline", {"Code" : self.disciplin, "IFId" : team_id})
            event_elem = ET.SubElement(dis_elem, "RegisteredEvent", {"Event" : self.get_discipline_code(category)})

            self.accreditation_id += 1
        if type(participant) == model.ParticipantTeam:
            team_attrib = {
                "Code" : str(self.accreditation_id),
                "Organisation" : participant.team.club.nation,
                "Number" : "1",
                "Name" : participant.team.name,
                "ShortName" : participant.team.name,
                "TeamType" : "CUSTOM",
                "TVTeamName" : participant.team.name,
                "Gender" : "X",
                "Current" : "true",
                "ModificationIndicator" : "N"
                }
            team_elem = ET.SubElement(self.competition_elem_couples, "Team", team_attrib)

            dis_elem = ET.SubElement(team_elem, "Discipline", {"Code" : self.disciplin, "IFId" : participant.team.id})
            event_elem = ET.SubElement(dis_elem, "RegisteredEvent", {"Event" : self.get_discipline_code(category)})
            event_club_attrib = {
                "Type" : "ER_EXTENDED",
                "Code" : "CLUB"
            }
            ET.SubElement(event_elem, "EventEntry", {**event_club_attrib, **{"Pos" : "1", "Value" : participant.team.club.name}})
            ET.SubElement(event_elem, "EventEntry", {**event_club_attrib, **{"Pos" : "2", "Value" : participant.team.club.abbr}})
            self.accreditation_id += 1

    def add_person(self, person: model.Person) -> None:
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
            "BirthDate" : person.bday.strftime('%Y-%m-%d') if person.bday else "",
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
            time = now.strftime("%H%M%S%f")[:9]
            competition_attrib = {
                "CompetitionCode" : self.competition.name if self.competition else "Test",
                "DocumentCode" : self.disciplin,
                "DocumentType" : "DT_PARTIC",
                "Version" : "1",
                "FeedFlag" : "P",
                "Date" : date,
                "Time" : time,
                "LogicalDate" : date,
                "Source" : "FSKFSK1"
            }

            def write_xml(path: pathlib.Path, root: ET.Element, name: str) -> None:
                xmlstr = minidom.parseString(ET.tostring(root, xml_declaration= True)).toprettyxml(indent="  ")
                with open(str(path / name), "w", encoding="utf-8") as f:
                    f.write(xmlstr)

            root = ET.Element("OdfBody", competition_attrib)
            root.insert(0, self.competition_elem)
            write_xml(self.path, root, "DT_PARTIC.xml")

            competition_attrib["DocumentType"] = "DT_PARTIC_TEAMS"
            root = ET.Element("OdfBody", competition_attrib)
            root.insert(0, self.competition_elem_couples)
            write_xml(self.path, root, "DT_PARTIC_TEAMS.xml")

        else:
            print("OdfParticOutput: No persons found for writing. Skip creating file.")

    @staticmethod
    def get_discipline_code(category: model.Category):

        code = "FSK" + category.gender.ODF() + category.type.ODF()
        code += "-" * (12 - len(code))
        code += category.level.ODF()
        code += "-" * (20 - len(code))
        code += "%02d" % category.number if category.number else "--"

        # add trailing dashes (discipline code always consists of 34 characters)
        code += "-" * (34 - len(code))
        return code
