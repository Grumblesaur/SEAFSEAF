import pandas
import utils
import os
from pprint import pprint
from collections import defaultdict
from pathlib import Path

from exceptions import UnknownEquipment


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
        self.primaries = {'types': defaultdict(set), 'functions': defaultdict(set), 'all': set()}
        for name, ptype, functions, source in primaries:
            self.primaries['types'][ptype].add(name)
            for function in functions:
                self.primaries['functions'][function].add(name)
            self.primaries['all'].add(name)

        secondaries = self._load_personal(pandas.read_excel(source_ods, "Secondary"))
        self.secondaries = {'types': defaultdict(set), 'functions': defaultdict(set), 'all': set()}
        for name, stype, functions, source in secondaries:
            self.secondaries['types'][stype].add(name)
            for function in functions:
                self.secondaries['functions'][function].add(name)
            self.secondaries['all'].add(name)

        throwables = self._load_personal(pandas.read_excel(source_ods, "Throwable"))
        self.throwable = {'types': defaultdict(set), 'functions': defaultdict(set), 'all': set()}
        for name, stype, functions, source in throwables:
            self.throwable['types'][stype].add(name)
            for function in functions:
                self.throwable['functions'][function].add(name)
            self.throwable['all'].add(name)

        stratagems = self._load_stratagems(pandas.read_excel(source_ods, "Stratagems"))
        self.stratagems = {'types': defaultdict(set), 'subtypes': defaultdict(set), 'functions': defaultdict(set), 'all': set()}
        for name, stype, subtypes, functions, source in stratagems:
            self.stratagems['types'][stype].add(name)
            for subtype in subtypes:
                self.stratagems['subtypes'][subtype].add(name)
            for function in functions:
                self.stratagems['functions'][function].add(name)
            self.stratagems['all'].add(name)

        self.boosters = {'all': {name for name, _ in self._load_boosters(pandas.read_excel(source_ods, "Booster"))}}

        armor = self._load_armor(pandas.read_excel(source_ods, 'Armor'))
        self.armor = {'passives': defaultdict(set), 'weights': defaultdict(set), 'all': set()}
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


    def has(self, slot_type: str, item_name: str) -> bool:
        match slot_type:
            case "Primary":
                return item_name in self.primaries['all']
            case "Secondary":
                return item_name in self.secondaries['all']
            case "Throwable":
                return item_name in self.throwable['all']
            case "Stratagems":
                return item_name in self.stratagems['all']
            case "Booster":
                return item_name in self.boosters['all']
            case "Armor":
                return item_name in self.armor['all']
            case _:
                raise UnknownEquipment(f"Unrecognized equipment slot: {slot_type!r}")
