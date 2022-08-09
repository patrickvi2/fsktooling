import datetime
from enum import Enum, IntEnum
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

class DataSource(IntEnum):
    FSM =  0
    CALC = 1
    ODF =  2
    DEU =  3


class DataEnum(Enum):
    @classmethod
    def from_value(cls, value, data_source: DataSource):
        cls.check_data_source(data_source)
        for member in cls.__members__.values():
            if member.value[data_source] == value:
                return member
    
    @staticmethod
    def check_data_source(data_source: DataSource):
        pass

    def __str__(self) -> str:
        return self.name.lower()

    def getvalue(self, data_source: DataSource):
        self.check_data_source(data_source)
        return self.value[data_source]

    def FSM(self) -> int:
        return self.getvalue(DataSource.FSM)
    def CALC(self) -> str:
        return self.getvalue(DataSource.CALC)
    def ODF(self) -> str:
        return self.getvalue(DataSource.ODF)
    def DEU(self) -> str:
        return self.getvalue(DataSource.DEU)

class Gender(DataEnum):
    MALE = (0, 'M', 'M')
    FEMALE = (1, 'F', 'W')
    TEAM = (2, 'T', 'X')

    @staticmethod
    def check_data_source(data_source: DataSource):
        if data_source == DataSource.DEU:
            raise Exception("Invalid input data source.")

class Person:
    def __init__(self) -> None:
        self.id = ''
        self.first_name = ''
        self.family_name = ''
        self.gender = Gender.FEMALE
        self.bday = datetime.date()
        self.club = Club()

    def __init__(self, id, family_name, first_name, gender: Gender, birthday: datetime.date, club: Club) -> None:
        self.id = id  # DEU ID or "Sportpassnummer"
        self.first_name = first_name
        self.family_name = family_name
        self.gender = gender
        self.bday = birthday
        self.club = club

class SegmentType(DataEnum):
    SP = (0, 'S', 'QUAL')
    FP = (1, 'F', 'FNL')
    PD = (2, 'P', 'QUAL')

    @staticmethod
    def check_data_source(data_source: DataSource):
        if data_source == DataSource.DEU:
            raise Exception("Invalid input data source.")

class Segment:
    def __init__(self, name: str, abbreviation: str, type: SegmentType) -> None:
        self.name = name
        self.abbr = abbreviation
        self.type = type

class CategoryType(DataEnum):
    MEN = (0, 'S', 'SINGLES', 'Herren')
    WOMEN = (1, 'S', 'SINGLES', 'Damen')
    PAIRS = (2, 'P', 'PAIRS', 'Paarlaufen')
    ICEDANCE = (3, 'D', 'ICEDANCE', 'Eistanzen')
    SYNCHRON = (4, 'T', 'SYNCHRON', 'Synchron')

class CategoryLevel(DataEnum):
    SENIOR = (0, 'S', '', 'Meisterklasse')
    JUNIOR = (1, 'J', 'JUNIOR', 'Juniorenklasse')
    JUGEND = (None, 'J', 'JUNIOR', 'Jugendklasse')
    NOVICE_ADVANCED = (2, 'V', 'ADVANOVICE', 'Nachwuchsklasse')
    NOVICE_INTERMEDIATE = (3, 'I', 'INTENOVICE', 'Nachwuchsklasse')
    NOVICE_BASIC = (4, 'R', 'BASENOVICE', 'Nachwuchsklasse')
    ADULT = (5, 'O', 'ADULT', 'Adult')
    MIXEDAGE = (6, 'O', 'MIXEDAGE', '')
    OTHER = (None, 'O', '', 'Sonstige Wettbewerbe')
    NOTDEFINED = (None, 'O', '', 'nicht definiert')

    def is_ISU_category(self) -> bool:
        return self.FSM() is not None

class Category:
    def __init__(self, name: str, category_type: CategoryType, category_level: CategoryLevel, gender: Gender) -> None:
        self.name = name
        self.type = category_type
        self.level = category_level
        self.gender = gender
        self.segments = []
    
    def add_segment(self, segment: Segment):
        self.segments.append(segment)

class Couple:
    def __init__(self, partner_1: Person, partner_2: Person) -> None:
        self.partner_1 = partner_1
        self.partner_2 = partner_2
class Team:
    def __init__(self, id, name: str, club: Club, persons: List[Person]) -> None:
        self.id = id
        self.name = name # could be sys team name or couple name
        self.club = club # also holds the nation
        self.persons = persons # for couples or SYS
class ParticipantBase:
    def __init__(self, category: Category, status = None, total_points = None) -> None:
        self.cat = category
        self.status = status
        self.points = total_points

class ParticipantSingle(ParticipantBase):
    def __init__(self, person: Person, category: Category, status=None, total_points=None) -> None:
        super().__init__(category, status, total_points)
        self.person = person

class ParticipantCouple(ParticipantBase):
    def __init__(self, couple: Couple, category: Category, status=None, total_points=None) -> None:
        super().__init__(category, status, total_points)
        self.couple = couple

class ParticipantTeam(ParticipantBase):
    def __init__(self, team: Team, category: Category, status=None, total_points=None) -> None:
        super().__init__(category, status, total_points)
        self.team = team

if __name__ == "__main__":
    print(Gender.MALE)
    g = Gender.from_value('F', DataSource.CALC)
    print(g)
    print(g.FSM())
    Gender.from_value('Herrn', DataSource.DEU)
