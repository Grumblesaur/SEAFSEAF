from typing import Iterator, Iterable

import pandas
import utils
import os
from pprint import pprint
from collections import defaultdict
from pathlib import Path

from equipment import RegPreset, Slot, Source


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

    def register_sources(self, user_handle: str, sources: Iterable[Source], catalog: EquipmentCatalog):
        self._save_user_registration(user_handle, self._get_owned_equipment(sources, catalog))

    def _save_user_registration(self, user_handle: str, owned_equipment: dict[str, set[str]]):
        with open(self.user_path(user_handle), 'w', encoding='utf-8') as f:
            pprint(owned_equipment, f)
        self.registered.add(user_handle)

    @staticmethod
    def _get_owned_equipment(sources: Iterable[Source], catalog: EquipmentCatalog) -> dict[str, set[str]]:
        owned_equipment = defaultdict(set)
        sources = list(sources)
        Source.replace_shorthand(sources)
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
        self.boosters: dict = {'all': set(), 'sources': defaultdict(set),
                               'functions': defaultdict(set)}
        for name, functions, source in boosters:
            self.boosters['all'].add(name)
            self.boosters['sources'][source].add(name)
            for function in functions:
                self.boosters['functions'][function].add(name)


        armor = self._load_armor(pandas.read_excel(source_ods, 'Armor'))
        self.armor: dict = {'passives': defaultdict(set),
                            'weights': defaultdict(set),
                            'functions': defaultdict(set),
                            'sources': defaultdict(set),
                            'all': set()}
        for name, weight, passive, functions, source in armor:
            self.armor['all'].add(name)
            self.armor['sources'][source].add(name)
            self.armor['weights'][weight].add(name)
            self.armor['passives'][passive].add(name)
            for function in functions:
                self.armor['functions'][function].add(name)


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
        for index, (_, name, functions, source) in dataframe.iterrows():
            boosters.append((name, tuple(functions.split(';')), source))
        return boosters

    @staticmethod
    def _load_armor(dataframe: pandas.DataFrame) -> list[tuple[str, ...]]:
        """Works for armor."""
        armor = []
        for index, (_, name, weight, passive, function, source) in dataframe.iterrows():
            armor.append((name, weight, passive, tuple(function.split(';')), source))
        return armor


    def has(self, slot: str, item_name: str) -> bool:
        slot_type = Slot.from_string(slot)
        match slot_type:
            case Slot.Primary:
                return item_name in self.primaries['all']
            case Slot.Secondary:
                return item_name in self.secondaries['all']
            case Slot.Throwable:
                return item_name in self.throwable['all']
            case Slot.Stratagem:
                return item_name in self.stratagems['all']
            case Slot.Booster:
                return item_name in self.boosters['all']
            case Slot.Armor:
                return item_name in self.armor['all']
