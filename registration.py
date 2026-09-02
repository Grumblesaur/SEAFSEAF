from typing import Iterator, Iterable

import pandas
import utils
import os
from pprint import pprint
from collections import defaultdict
from pathlib import Path
from enum import IntEnum, StrEnum, nonmember

from exceptions import UnknownSlot, StratagemSubtypeMismatch, UnknownRegistrationPreset, UnknownEquipmentSource


class EqSource(StrEnum):
    # Included with the game
    Stock = 'Default Equipment'
    HM = 'Helldivers Mobilize'
    EV = 'Event Rewards'

    # Standard warbonds
    SV = 'Steeled Veterans'
    CE = 'Cutting Edge'
    DD = 'Democratic Detonation'
    PP = 'Polar Patriots'
    VC = 'Viper Commandos'
    FF = "Freedom's Flame"
    CA = 'Chemical Agents'
    TE = 'Truth Enforcers'
    UL = 'Urban Legends'
    SF = 'Servants of Freedom'
    BJ = 'Borderline Justice'
    MC = 'Masters of Ceremony'
    FL = 'Force of Law'
    CG = 'Control Group'
    DUDE = 'Dust Devils'
    PC = 'Python Commandos'
    RR = 'Redacted Regiment'
    SB = 'Siege Breakers'
    ED = 'Entrenched Division'
    EE = 'Exo Experts'

    # Legendary warbonds
    ODST = 'Obedient Democracy Support Troopers'
    KZ = 'Righteous Revenants'
    WH = "Castellan's Creed"

    # Premium content
    SCE = 'Super Citizen Edition'
    SS = 'Super Store'
    PB = 'Preorder Bonus'

    # Super destroyer
    PAC = 'Patriotic Administration Center'
    EB = 'Engineering Bay'
    HG = 'Hangar'
    BR = 'Bridge'
    RW = 'Robotics Workshop'
    OC = 'Orbital Cannons'
    SDD = 'Combines `PAC`, `EB`, `HG`, `BR`, `RW`, and `OC`'

    @classmethod
    def from_string(cls, equipment_source: str):
        s = equipment_source.casefold()
        # Included with the game
        if prefix_match(cls.Stock, s):        return cls.Stock
        if prefix_match(cls.HM, s):           return cls.HM
        if prefix_match(cls.EV, s):           return cls.EV

        # Standard warbonds
        if prefix_match(cls.BJ, s):           return cls.BJ
        if prefix_match(cls.CA, s):           return cls.CA
        if prefix_match(cls.CE, s):           return cls.CE
        if prefix_match(cls.CG, s):           return cls.CG
        if prefix_match(cls.DD, s, 'DEDE'):   return cls.DD
        if prefix_match(cls.DUDE, s, 'DUST'): return cls.DUDE
        if prefix_match(cls.ED, s):           return cls.ED
        if prefix_match(cls.EE, s):           return cls.EE
        if prefix_match(cls.FF, s):           return cls.FF
        if prefix_match(cls.FL, s, 'FOL'):    return cls.FL
        if prefix_match(cls.MC, s, 'MOC'):    return cls.MC
        if prefix_match(cls.PC, s):           return cls.PC
        if prefix_match(cls.PP, s):           return cls.PP
        if prefix_match(cls.RR, s, 'RERE'):   return cls.RR
        if prefix_match(cls.SB, s):           return cls.SB
        if prefix_match(cls.SF, s, 'SOF'):    return cls.SF
        if prefix_match(cls.SV, s):           return cls.SV
        if prefix_match(cls.TE, s):           return cls.TE
        if prefix_match(cls.UL, s):           return cls.UL
        if prefix_match(cls.VC, s):           return cls.VC

        # Legendary warbonds
        if prefix_match(cls.KZ, s, 'Killzone', 'RIRE'):
            return cls.KZ
        if prefix_match(cls.ODST, s, 'HALO'):
            return cls.ODST
        if prefix_match(cls.WH, s, 'WH', 'Warhammer', 'WH40K', '40K'):
            return cls.WH

        # Premium content
        if prefix_match(cls.SCE, s):          return cls.SCE
        if prefix_match(cls.SS, s):           return cls.SS
        if prefix_match(cls.PB, s):           return cls.PB

        # Super destroyer
        if prefix_match(cls.PAC, s):          return cls.PAC
        if prefix_match(cls.EB, s):           return cls.EB
        if prefix_match(cls.HG, s):           return cls.HG
        if prefix_match(cls.BR, s):           return cls.BR
        if prefix_match(cls.RW, s):           return cls.RW
        if prefix_match(cls.OC, s):           return cls.OC
        if prefix_match(cls.SDD, s, 'DDS', 'SD'):  # Shorthand for all Super Destroyer equipment
            return cls.SDD
        raise UnknownEquipmentSource(f'No matching equipment source for `{equipment_source}`. Use'
                                     f' the command `viewsources` for information on equipment availability.')

    @classmethod
    def replace_shorthand(cls, eq_sources: list[EqSource]):
        if cls.SDD in eq_sources:
            eq_sources.remove(cls.SDD)
            eq_sources.extend([cls.PAC, cls.EB, cls.HG, cls.BR, cls.RW, cls.OC])


def _initialize_presets(cls):
    cls._make_preset_sources()
    return cls


@_initialize_presets
class RegPreset(StrEnum):
    Classic = "OG"  # Stock equipment, event items, and Helldivers Mobilize! only
    Enthusiast = "ET"  # Classic + all non-legendary warbonds
    Collector = "CL"  # Enthusiast + all legendary warbonds
    Armorer = "AM"  # Collector + all superstore items
    Quartermaster = "QM"  # Armorer + Super Citizen edition + preorder items

    def description(self):
        match self:
            case self.Classic:
                d = "Default equipment, event rewards, super destroyer equipment, and Helldivers Mobilize"
            case self.Enthusiast:
                d = "All items from **Classic** + all non-legendary warbonds"
            case self.Collector:
                d = "All items from **Enthusiast** + all legendary warbonds"
            case self.Armorer:
                d = "All items from **Collector** + all Super Store items"
            case self.Quartermaster:
                d = "All items from **Armorer** + Super Citizen Edition + Preorder bonuses"
        return d

    PresetSources = nonmember(None)

    @classmethod
    def from_string(cls, preset_name: str):
        s = preset_name.casefold()
        if prefix_match(cls.Classic, s):
            return cls.Classic
        if prefix_match(cls.Enthusiast, s):
            return cls.Enthusiast
        if prefix_match(cls.Collector, s):
            return cls.Collector
        if prefix_match(cls.Armorer, s):
            return cls.Armorer
        if prefix_match(cls.Quartermaster, s):
            return cls.Quartermaster
        raise UnknownRegistrationPreset(f'No matching preset for `{preset_name}`.')

    def sources(self):
        return self.PresetSources[self]

    @classmethod
    def _make_preset_sources(cls):
        mapping = {cls.Classic: [EqSource.Stock, EqSource.EV, EqSource.HM, EqSource.SDD]}

        mapping[cls.Enthusiast] = mapping[cls.Classic] + [
            EqSource.BJ, EqSource.CA, EqSource.CE, EqSource.CE, EqSource.CG,
            EqSource.DD, EqSource.DUDE, EqSource.ED, EqSource.EE, EqSource.FF,
            EqSource.FL, EqSource.MC, EqSource.MC, EqSource.PC, EqSource.PP,
            EqSource.RR, EqSource.SB, EqSource.SF, EqSource.SV, EqSource.TE,
            EqSource.UL, EqSource.VC
        ]

        mapping[cls.Collector] = mapping[cls.Enthusiast] + [
            EqSource.KZ, EqSource.WH, EqSource.ODST,
        ]

        mapping[cls.Armorer] = mapping[cls.Collector] + [EqSource.SS]
        mapping[cls.Quartermaster] = mapping[cls.Armorer] + [
            EqSource.SCE, EqSource.PB,
        ]
        cls.PresetSources = mapping


class SlotType(IntEnum):
    Primary = 1
    Secondary = 2
    Throwable = 3
    Booster = 4
    Armor = 5
    Stratagem = 6

    @classmethod
    def from_string(cls, slot_name: str):
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
        try:
            self.registered = set()
            for user_file in os.listdir(self.directory):
                user_path = Path(user_file)
                handle = user_path.name.removesuffix(user_path.suffix)
                self.registered.add(handle)
        except FileNotFoundError:
            self.registered = set()
            os.makedirs(directory)

    def register(self, uploaded_workbook: Path, user_handle: str, catalog: EquipmentCatalog):
        owned_equipment = defaultdict(set)
        for slot_type, df in pandas.read_excel(uploaded_workbook, sheet_name=None).items():
            for index, (user_owns, item_name, *_) in df.iterrows():
                if not utils.isnan(user_owns) and catalog.has(slot_type, item_name):
                    owned_equipment[slot_type].add(item_name)
        self._save_user_registration(user_handle, dict(owned_equipment))

    def register_preset(self, user_handle: str, preset: RegPreset, catalog: EquipmentCatalog):
        self._save_user_registration(user_handle, self._get_owned_equipment(preset.sources(), catalog))

    def register_sources(self, user_handle: str, sources: Iterable[EqSource], catalog: EquipmentCatalog):
        self._save_user_registration(user_handle, self._get_owned_equipment(sources, catalog))

    def _save_user_registration(self, user_handle: str, owned_equipment: dict[str, set[str]]):
        with open(self.user_path(user_handle), 'w', encoding='utf-8') as f:
            pprint(owned_equipment, f)
        self.registered.add(user_handle)

    @staticmethod
    def _get_owned_equipment(sources: Iterable[EqSource], catalog: EquipmentCatalog) -> dict[str, set[str]]:
        owned_equipment = defaultdict(set)
        sources = list(sources)
        EqSource.replace_shorthand(sources)
        for slot_type, catalog_page in catalog:
            for source in sources:
                owned_equipment[slot_type].update(catalog_page['sources'][source])
        return dict(owned_equipment)

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
    def __iter__(self) -> Iterator[tuple[str, dict]]:
        yield 'Primary', self.primaries
        yield 'Secondary', self.secondaries
        yield 'Throwable', self.throwable
        yield 'Stratagems', self.stratagems
        yield 'Booster', self.boosters
        yield 'Armor', self.armor


    def __init__(self, source_ods: Path):
        primaries = self._load_personal(pandas.read_excel(source_ods, "Primary"))
        self.primaries: dict = {'types': defaultdict(set),
                                'functions': defaultdict(set),
                                'sources': defaultdict(set),
                                'all': set()}
        for name, ptype, functions, source in primaries:
            self.primaries['types'][ptype].add(name)
            self.primaries['sources'][source].add(name)
            for function in functions:
                self.primaries['functions'][function].add(name)
            self.primaries['all'].add(name)

        secondaries = self._load_personal(pandas.read_excel(source_ods, "Secondary"))
        self.secondaries: dict = {'types': defaultdict(set),
                                  'functions': defaultdict(set),
                                  'sources': defaultdict(set),
                                  'all': set()}
        for name, stype, functions, source in secondaries:
            self.secondaries['types'][stype].add(name)
            self.secondaries['sources'][source].add(name)
            for function in functions:
                self.secondaries['functions'][function].add(name)
            self.secondaries['all'].add(name)

        throwables = self._load_personal(pandas.read_excel(source_ods, "Throwable"))
        self.throwable: dict = {'types': defaultdict(set),
                                'functions': defaultdict(set),
                                'sources': defaultdict(set),
                                'all': set()}
        for name, stype, functions, source in throwables:
            self.throwable['types'][stype].add(name)
            self.throwable['sources'][source].add(name)
            for function in functions:
                self.throwable['functions'][function].add(name)
            self.throwable['all'].add(name)

        stratagems = self._load_stratagems(pandas.read_excel(source_ods, "Stratagems"))
        self.stratagems: dict = {'types': defaultdict(set),
                                 'subtypes': defaultdict(set),
                                 'functions': defaultdict(set),
                                 'sources': defaultdict(set),
                                 'all': set()}
        for name, stype, subtypes, functions, source in stratagems:
            self.stratagems['types'][stype].add(name)
            self.stratagems['sources'][source].add(name)
            for subtype in subtypes:
                self.stratagems['subtypes'][subtype].add(name)
            for function in functions:
                self.stratagems['functions'][function].add(name)
            self.stratagems['all'].add(name)

        boosters = self._load_boosters(pandas.read_excel(source_ods, "Booster"))
        self.boosters = {'all': set(), 'sources': defaultdict(set)}
        for name, source in boosters:
            self.boosters['all'].add(name)
            self.boosters['sources'][source].add(name)

        armor = self._load_armor(pandas.read_excel(source_ods, 'Armor'))
        self.armor: dict = {'passives': defaultdict(set),
                            'weights': defaultdict(set),
                            'sources': defaultdict(set),
                            'all': set()}
        for name, weight, passive, source in armor:
            self.armor['all'].add(name)
            self.armor['sources'][source].add(name)
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
        slot_type = SlotType.from_string(slot)
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
