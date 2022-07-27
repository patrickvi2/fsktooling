import datetime
from typing import List

class Club:
    def __init__(self) -> None:
        self.name = ''
        self.abbr = ''
        self.nation = ''
    
    def __init__(self, name: str, abbreviation: str, nation: str) -> None:
        self.name = name
        self.abbr = abbreviation
        self.nation = nation

class Person:
    def __init__(self) -> None:
        self.id = ''
        self.first_name = ''
        self.family_name = ''
        self.gender = ''
        self.bday = datetime.date()
        self.club = Club()

    def __init__(self, id, family_name, first_name, gender, birthday, club: Club) -> None:
        self.id = id  # DEU ID or "Sportpassnummer"
        self.first_name = first_name
        self.family_name = family_name
        self.gender = gender
        self.bday = birthday
        self.club = club

class Category:
    def __init__(self, name: str, category_type: str, category_level: str, gender: str) -> None:
        self.name = name
        self.type = category_type
        self.level = category_level
        self.gender = gender

class Couple:
    def __init__(self, partner_1, partner_2) -> None:
        self.partner_1 = partner_1
        self.partner_2 = partner_2
class Team:
    def __init__(self, id, name: str, club: Club, persons: List[Person]) -> None:
        self.id = id
        self.name = name # could be sys team name or couple name
        self.club = club # also holds the nation
        self.persons = persons # for couples or SYS
class ParticipantBase:
    def __init__(self, category, status = None, total_points = None) -> None:
        self.cat = category
        self.status = status
        self.points = total_points

class ParticipantSingle(ParticipantBase):
    def __init__(self, person, category, status=None, total_points=None) -> None:
        super().__init__(category, status, total_points)
        self.person = person

class ParticipantCouple(ParticipantBase):
    def __init__(self, couple, category, status=None, total_points=None) -> None:
        super().__init__(category, status, total_points)
        self.couple = couple

class ParticipantTeam(ParticipantBase):
    def __init__(self, team, category, status=None, total_points=None) -> None:
        super().__init__(category, status, total_points)
        self.team = team

