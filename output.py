import csv
import xml.etree.ElementTree as ET

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
        self.persons.append([person.first_name, person.family_name, person.gender, person.club.abbr, person.club.nation, person.id, bday])

    def write_file(self):
        if self.persons:
            with open(self.path, 'w') as f:
                w = csv.writer(f, delimiter='|')
                w.writerows(self.persons)


# participants
class ParticipantCsvOutput(OutputBase):
    def __init__(self, file_path: str):
        super().__init__(file_path)
        self.participants = list()

    def add_participant(self, participant: model.ParticipantBase):
        par_dict = {}
        # category 
        par_dict["Kategorie-Name"] = participant.cat.name
        par_dict["Kategorie-Typ"] = participant.cat.type
        par_dict["Kategorie-Geschlecht"] = participant.cat.gender
        par_dict["Kategorie-Level"] = participant.cat.level
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
        if type(participant) == model.ParticipantSingle:
            par_dict['Vorname'] = participant.person.first_name
            par_dict['Name'] = participant.person.family_name
            par_dict['Geburtstag'] = participant.person.bday.strftime('%d.%m.%Y')
            par_dict['Nation'] = participant.person.club.nation
            par_dict['Club-Name'] = participant.person.club.name
            par_dict['Club-Abk.'] = participant.person.club.abbr
        elif type(participant) == model.ParticipantTeam:
            par_dict['Team-Name'] = participant.team.name
            par_dict['Nation'] = participant.team.club.nation
            par_dict['Club-Name'] = participant.team.club.name
            par_dict['Club-Abk.'] = participant.team.club.abbr
        elif type(participant) == model.ParticipantCouple:
            p1 = participant.couple.partner_1
            p2 = participant.couple.partner_2
            par_dict['Vorname'] = p1.first_name
            par_dict['Name'] = p1.first_name
            par_dict['Vorname-Partner'] = p2.first_name
            par_dict['Name-Partner'] = p2.first_name
            par_team_name = '%s %s / %s %s' % (
                p1.first_name, 
                p1.family_name, 
                p2.first_name, 
                p2.family_name)
            if p1.club.abbr == p2.club.abbr: # same club
                par_team_club_name = p1.club.name
                par_team_club_abbr = p1.club.abbr
            else:
                par_team_club_name = p1.club.name + " / " + p2.club.name
                par_team_club_abbr = p1.club.abbr + " / " + p2.club.abbr

            if p1.club.nation == p2.club.nation:
                par_team_nation = p1.club.nation
            else:
                par_team_nation = p1.club.nation + " / " + p2.club.nation
            par_dict['Team-Name'] = par_team_name
            par_dict['Nation'] = par_team_nation
            par_dict['Club-Name'] = par_team_club_name
            par_dict['Club-Abk.'] = par_team_club_abbr


        self.participants.append(par_dict)

    def add_person(self, person: model.Person):
        pass

    def write_file(self):
        if self.participants:
            with open(self.path, 'w') as f:
                w = csv.DictWriter(f, self.participants[0].keys())
                w.writeheader()
                w.writerows(self.participants)


class OdfParticOutput(OutputBase):
    def __init__(self, file_path: str) -> None:
        super().__init__(file_path)
        self.competition_elem = ET.Element("Competition")
        self.disciplin = "FSK" + 31 * "-"
        self.event_singles = "FSKMSINGLES" + 23 * "-"
    
    def add_participant(self, participant: model.ParticipantBase):
        pass

    def add_person(self, person: model.Person):
        first = person.first_name
        last = person.family_name
        participant_attrib = {
            "Status" : "ACTIVE",
            "GivenName" : first,
            "FamilyName" : last,
            "PrintName" : f"{first} {last.upper()}",
            "PrintInitialName" : f"{first[0]} {last.upper()}",
            "TVName" : f"{first} {last.upper()}",
            "TVInitialName" : f"{first[0]}. {last.upper()}",
            "Gender" : person.gender,
            "Organisation" : "",
            "BirthDate" : person.bday.strftime('%Y-%m-%d'),
            "Height" : "-",
            "Current" : "true",
            "ModificationIndicator" : "N"
            }
        par_elem = ET.SubElement(self.competition_elem, "Participant", attrib=participant_attrib)
        dis_elem = ET.SubElement(par_elem, "Discipline", {"Code" : self.disciplin, "IFId" : person.id})
        event_elem = ET.SubElement(dis_elem, "RegisteredEvent", {"Event" : self.event_singles})
        event_club_attrib = {
            "Type" : "ER_EXTENDED",
            "Code" : "CLUB"
        }
        ET.SubElement(event_elem, "EventEntry", {**event_club_attrib, **{"Pos" : "1", "Value" : person.club.name}})
        ET.SubElement(event_elem, "EventEntry", {**event_club_attrib, **{"Pos" : "2", "Value" : person.club.abbr}})

    def write_file(self):
        if len(self.competition_elem) > 0:
            competition_attrib = {
                "CompetitionCode" : "TestName",
                "DocumentCode" : self.disciplin,
                "DocumentType" : "DT_PARTIC_UPDATE",
                "Version" : "1",
                "FeedFlag" : "P",
                "Date" : "2022-01-01",
                "Time" : "123456789",
                "LogicalDate" : "2022-01-01",
                "Source" : "FSKFSK1"
            }
            root = ET.Element("OdfBody", competition_attrib)
            root.insert(0, self.competition_elem)
            ET.ElementTree(root).write(self.path, encoding="utf-8", xml_declaration=True)
        else:
            print("OdfParticOutput: No persons found for writing. Skip creating file.")