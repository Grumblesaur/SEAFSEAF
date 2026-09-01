import pandas
import utils
import os
from pprint import pprint
from collections import defaultdict
from pathlib import Path
from enum import IntEnum, StrEnum, IntFlag

from exceptions import UnknownSlot, StratagemSubtypeMismatch


class SlotType(IntEnum):
    Primary = 1
    Secondary = 2
    Throwable = 3
    Booster = 4
    Armor = 5
    Stratagem = 6

    @classmethod
    def from_name(cls, slot_name: str):
        slot_name = slot_name.capitalize()
        if "Primary".startswith(slot_name) or "Primaries".startswith(slot_name):
            return cls.Primary
        if "Secondary".startswith(slot_name) or "Secondaries".startswith(slot_name):
            return cls.Secondary
        if "Throwables".startswith(slot_name):
            return cls.Throwable
        if "Boosters".startswith(slot_name):
            return cls.Booster
        if "Armor".startswith(slot_name):
            return cls.Armor
        if "Stratagems".startswith(slot_name):
            return cls.Stratagem
        raise UnknownSlot(f"No matching slot type found for {slot_name!r}.")


def prefix_match(str_enum, casefolded_user_input: str, *extras):
    if str_enum.name.casefold().startswith(casefolded_user_input):
        return True
    if str_enum.value.casefold().startswith(casefolded_user_input):
        return True
    for ex in extras:
        if ex.casefold().startswith(casefolded_user_input):
            return True
    return False


class PrimaryType(StrEnum):
    AssaultRifle = "Assault Rifle"
    MarksmanRifle = "Marksman Rifle"
    SubmachineGun = "Submachine Gun"
    Shotgun = "Shotgun"
    Explosive = "Explosive"
    EnergyBased = "Energy-Based"
    Special = "Special"

    @classmethod
    def from_string(cls, primary_type: str):
        s = primary_type.casefold()
        if prefix_match(cls.AssaultRifle, s, 'AR'):
            return cls.AssaultRifle
        if prefix_match(cls.MarksmanRifle, s, 'MR'):
            return cls.MarksmanRifle
        if prefix_match(cls.SubmachineGun, s, 'SMG'):
            return cls.SubmachineGun
        if prefix_match(cls.Shotgun, s, 'SG'):
            return cls.Shotgun
        if prefix_match(cls.Explosive, s):
            return cls.Explosive
        if prefix_match(cls.EnergyBased, s, 'EB'):
            return cls.EnergyBased
        return cls.Special


class SecondaryType(StrEnum):
    Pistol = "Pistol"
    Melee = "Melee"
    Special = "Special"

    @classmethod
    def from_string(cls, secondary_type: str):
        s = secondary_type.casefold()
        if prefix_match(cls.Pistol, s):
            return cls.Pistol
        if prefix_match(cls.Melee, s):
            return cls.Melee
        return cls.Special


class ThrowableType(StrEnum):
    Standard = 'Standard'
    Special = 'Special'

    @classmethod
    def from_string(cls, throwable_type: str):
        s = throwable_type.casefold()
        if prefix_match(cls.Standard, s, 'std'):
            return cls.Standard
        return cls.Special


class StratagemType(StrEnum):
    Supply = 'Supply'
    Vehicle = 'Vehicle'
    Defensive = 'Emplacement'
    Offensive = 'Offensive'

    @classmethod
    def from_string(cls, stratagem_type: str):
        s = stratagem_type.casefold()
        if prefix_match(cls.Offensive, s, 'Offense'):
            return cls.Offensive
        if prefix_match(cls.Defensive, s, 'Defense', 'Defence'):
            return cls.Defensive
        if prefix_match(cls.Vehicle, s):
            return cls.Vehicle
        if prefix_match(cls.Supply, s):
            return cls.Supply
        return None

    def _valid_subtypes(self) -> set[StratagemSubtype]:
        if self is self.Supply:
            return {StratagemSubtype.Weapon, StratagemSubtype.Backpack, StratagemSubtype.BackpackWeapon}
        if self is self.Defensive:
            return {StratagemSubtype.Automated, StratagemSubtype.Manned, StratagemSubtype.Minefield}
        if self is self.Vehicle:
            return {StratagemSubtype.Car, StratagemSubtype.Exosuit, StratagemSubtype.Tank}
        if self is self.Offensive:
            return {StratagemSubtype.Orbital, StratagemSubtype.Aerial}
        return set()

    def validate_subtype(self, subtype: StratagemSubtype):
        if subtype not in (valid := self._valid_subtypes()):
            formatted = utils.format_series(map(lambda se: se.name, valid))
            raise StratagemSubtypeMismatch(f'Stratagem type {self.name} has no subtype {subtype.name}.'
                                           f' Valid subtypes include {formatted}')
        return True

class StratagemSubtype(StrEnum):
    Weapon = 'Weapon'
    Backpack = 'Kit'
    BackpackWeapon = 'KitWeapon'
    Exosuit = 'Mech'
    Car = 'FRV'
    Tank = 'Tank'
    Automated = 'Sentry'
    Manned = 'Emplacement'
    Minefield = 'Mines'
    Aerial = 'Eagle'
    Orbital = 'SuperDestroyer'

    @classmethod
    def from_string(cls, stratagem_subtype: str):
        s = stratagem_subtype.casefold()
        if prefix_match(cls.Backpack, s, 'Pack', 'Kit', 'BP'):
            return cls.Backpack
        if prefix_match(cls.BackpackWeapon, s, 'BW', 'BPW', 'KitWeapon'):
            return cls.BackpackWeapon
        if prefix_match(cls.Exosuit, s, 'Walker'):
            return cls.Exosuit
        if prefix_match(cls.Car, s):
            return cls.Car
        if prefix_match(cls.Tank, s):
            return cls.Tank
        if prefix_match(cls.Automated, s):
            return cls.Automated
        if prefix_match(cls.Manned, s):
            return cls.Manned
        if prefix_match(cls.Minefield, s):
            return cls.Minefield
        if prefix_match(cls.Orbital, s):
            return cls.Orbital
        if prefix_match(cls.Aerial, s):
            return cls.Aerial
        if prefix_match(cls.Weapon, s):
            return cls.Weapon
        return None


class ArmorWeight(StrEnum):
    Light = 'LT'
    Medium = 'MD'
    Heavy = 'HVY'

    @classmethod
    def from_string(cls, armor_weight: str):
        s = armor_weight.casefold()
        if prefix_match(cls.Light, s, 'Lite'):
            return cls.Light
        if prefix_match(cls.Medium, s):
            return cls.Medium
        if prefix_match(cls.Heavy, s):
            return cls.Heavy
        return None


class PlayerRegistry:
    def __init__(self, directory: Path):
        self.directory = directory
        self.registered = {Path(user_file).name for user_file in os.listdir(self.directory)}

    def register(self, uploaded_workbook: Path, user_handle: str, catalog: EquipmentCatalog):
        owned_equipment = defaultdict(set)
        for slot_type, df in pandas.read_excel(uploaded_workbook, sheet_name=None):
            for index, (user_owns, item_name, *_) in df.iterrows():
                if not utils.isnan(user_owns) and catalog.has(slot_type, item_name):
                    owned_equipment[slot_type].add(item_name)
        with open(self.user_path(user_handle), 'w', encoding='utf-8') as f:
            pprint(dict(owned_equipment), f)
        self.registered.add(user_handle)

    def unregister(self, user_handle: str):
        self.user_path(user_handle).unlink(missing_ok=True)
        self.registered.discard(user_handle)

    def __contains__(self, user_handle: str) -> bool:
        return user_handle in self.registered

    def user_path(self, user_handle) -> Path:
        return self.directory / f'{user_handle}.txt'

    def fetch_equipment(self, user_handle):
        with open(self.user_path(user_handle), 'r', encoding='utf-8') as f:
            return eval(f.read())


class EquipmentCatalog:
    def __init__(self, source_ods: Path):
        primaries = self._load_personal(pandas.read_excel(source_ods, "Primary"))
        self.primaries: dict = {'types': defaultdict(set),
                                'functions': defaultdict(set),
                                'all': set()}
        for name, ptype, functions, source in primaries:
            self.primaries['types'][ptype].add(name)
            for function in functions:
                self.primaries['functions'][function].add(name)
            self.primaries['all'].add(name)

        secondaries = self._load_personal(pandas.read_excel(source_ods, "Secondary"))
        self.secondaries: dict = {'types': defaultdict(set),
                                  'functions': defaultdict(set),
                                  'all': set()}
        for name, stype, functions, source in secondaries:
            self.secondaries['types'][stype].add(name)
            for function in functions:
                self.secondaries['functions'][function].add(name)
            self.secondaries['all'].add(name)

        throwables = self._load_personal(pandas.read_excel(source_ods, "Throwable"))
        self.throwable: dict = {'types': defaultdict(set),
                                'functions': defaultdict(set),
                                'all': set()}
        for name, stype, functions, source in throwables:
            self.throwable['types'][stype].add(name)
            for function in functions:
                self.throwable['functions'][function].add(name)
            self.throwable['all'].add(name)

        stratagems = self._load_stratagems(pandas.read_excel(source_ods, "Stratagems"))
        self.stratagems: dict = {'types': defaultdict(set),
                                 'subtypes': defaultdict(set),
                                 'functions': defaultdict(set),
                                 'all': set()}
        for name, stype, subtypes, functions, source in stratagems:
            self.stratagems['types'][stype].add(name)
            for subtype in subtypes:
                self.stratagems['subtypes'][subtype].add(name)
            for function in functions:
                self.stratagems['functions'][function].add(name)
            self.stratagems['all'].add(name)

        self.boosters = {'all': {name for name, _ in self._load_boosters(pandas.read_excel(source_ods, "Booster"))}}

        armor = self._load_armor(pandas.read_excel(source_ods, 'Armor'))
        self.armor: dict = {'passives': defaultdict(set),
                            'weights': defaultdict(set),
                            'all': set()}
        for name, weight, passive, source in armor:
            self.armor['all'].add(name)
            self.armor['weights'][weight].add(name)
            self.armor['passives'][passive].add(name)


    @staticmethod
    def _load_personal(dataframe: pandas.DataFrame) -> list[tuple[str, ...]]:
        """Works for primary, secondary, and throwable weapons."""
        weapons = []
        for index, (_, name, ptype, functions, source) in dataframe.iterrows():
            weapons.append((name, ptype, tuple(functions.split(';')), source))
        return weapons

    @staticmethod
    def _load_stratagems(dataframe: pandas.DataFrame) -> list[tuple[str, ...]]:
        """Works for stratagems."""
        stratagems = []
        for index, (_, name, stype, subtypes, functions, source) in dataframe.iterrows():
            stratagems.append((name, stype, tuple(subtypes.split(';')), tuple(functions.split(';')), source))
        return stratagems

    @staticmethod
    def _load_boosters(dataframe: pandas.DataFrame) -> list[tuple[str, ...]]:
        """Works for boosters."""
        boosters = []
        for index, (_, name, source) in dataframe.iterrows():
            boosters.append((name, source))
        return boosters

    @staticmethod
    def _load_armor(dataframe: pandas.DataFrame) -> list[tuple[str, ...]]:
        """Works for armor."""
        armor = []
        for index, (_, name, weight, passive, source) in dataframe.iterrows():
            armor.append((name, weight, passive, source))
        return armor


    def has(self, slot: str, item_name: str) -> bool:
        slot_type = SlotType.from_name(slot)
        match slot_type:
            case SlotType.Primary:
                return item_name in self.primaries['all']
            case SlotType.Secondary:
                return item_name in self.secondaries['all']
            case SlotType.Throwable:
                return item_name in self.throwable['all']
            case SlotType.Stratagem:
                return item_name in self.stratagems['all']
            case SlotType.Booster:
                return item_name in self.boosters['all']
            case SlotType.Armor:
                return item_name in self.armor['all']
