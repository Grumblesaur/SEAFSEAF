import operator
from collections import Counter
import datetime
from enum import IntEnum
from pathlib import Path
from inventory import Inventory, Everything, DefaultDiver, ByStyle
import random
from equipment import Style, Slot, EquipmentItem, Booster, StratagemSubtype, StratagemType, Primary, Secondary, \
    Throwable, Stratagem
from typing import TypeVar, Iterable

T = TypeVar('T')


class InventoryDatabase:
    def __init__(self, path: Path):
        self.path = path
        self.cache = dict[str, Inventory]
        self.last_time_used = dict[str, datetime.datetime]()

    def user_path(self, handle: str) -> Path:
        return self.path / f'{handle}.txt'

    def fetch(self, handle: str) -> Inventory:
        if (cached := self.cache.get(handle), None) is not None:
            self.last_time_used[handle] = datetime.datetime.now()
            return cached
        with open(self.user_path(handle), 'r', encoding='utf-8') as f:
            return eval(f.read())


class ArmorMode(IntEnum):
    Include = 1
    Exclude = 0

    def operation(self):
        if self is self.Include:
            return operator.and_
        return operator.sub


class Loadout:
    def __init__(self, loadout_pool: Inventory, vehicles: int = 1, backpacks: int = 1, support_weapons: int = 1,
                 used_boosters: set[Booster] | None = None):
        used_boosters = used_boosters or set()
        self.vehicles = vehicles
        self.backpacks = backpacks
        self.support_weapons = support_weapons
        self.equipment_pool = loadout_pool
        self.slots_defaulted = set()
        self.primary = self._get_primary()
        self.secondary = self._get_secondary()
        self.throwable = self._get_throwable()
        self.stratagem = self._get_stratagems()
        self.booster = self._get_booster(used_boosters)
        self.armor = self._get_armor()
        used_boosters.add(self.booster)

    def format(self, name: str) -> str:
        return f'{name}, your loadout is:\n{self}'

    def __str__(self):
        return '\n'.join([
            f'- **Primary{" [!]" if Slot.Primary in self.slots_defaulted else ""}:** `{self.primary}`',
            f'- **Secondary{" [!]" if Slot.Secondary in self.slots_defaulted else ""}:** `{self.secondary}`',
            f'- **Throwable{" [!]" if Slot.Throwable in self.slots_defaulted else ""}:** `{self.throwable}`',
            f'- **Stratagem{" [!]" if Slot.Stratagem in self.slots_defaulted else ""}:** `{self.stratagem}`',
            f'- **Booster{" [!]" if Slot.Booster in self.slots_defaulted else ""}:** `{self.booster}`',
            f'- **Armor**{" [!]" if Slot.Armor in self.slots_defaulted else ""}:&& `{self.armor}`',
        ])

    def _non_armor_items(self) -> Iterable[tuple[EquipmentItem, int]]:
        yield self.primary, 3
        yield self.secondary, 2
        yield self.throwable, 1
        for strat in self.stratagem:
            yield strat, 1
        yield self.booster, 2

    def _get_booster(self, used_boosters) -> Booster:
        if not (boosters := self.equipment_pool.booster - used_boosters):
            items, counts = DefaultDiver.booster_counts(used_boosters)
            return random.sample(items, counts=counts, k=1)
        return random.choice(list(boosters))


    def _get_personal(self, slot: Slot) -> EquipmentItem:
        attr = {Slot.Primary: 'primary',
                Slot.Secondary: 'secondary',
                Slot.Throwable: 'throwable'}
        if weapons := getattr(self.equipment_pool, attr[slot]):
            return random.choice(list(weapons))
        items, counts = DefaultDiver.randomization_counts(slot)
        self.slots_defaulted.add(slot)
        return random.sample(items, counts=counts, k=1)[0]

    # noinspection bad-return
    def _get_primary(self) -> Primary:
        return self._get_personal(Slot.Primary)

    # noinspection bad-return
    def _get_secondary(self) -> Secondary:
        return self._get_personal(Slot.Secondary)

    # noinspection bad-return
    def _get_throwable(self) -> Throwable:
        return self._get_personal(Slot.Throwable)

    def _get_stratagems(self) -> list[Stratagem]:
        backpacks = self.equipment_pool.filter_stratagems(by_subtype=StratagemSubtype.Backpack) or set()
        support_weapons = self.equipment_pool.filter_stratagems(by_subtype=StratagemSubtype.Weapon) or set()
        backpack_weapons = self.equipment_pool.filter_stratagems(by_subtype=StratagemSubtype.BackpackWeapon) or set()
        vehicles = self.equipment_pool.filter_stratagems(by_types=[StratagemType.Vehicle]) or set()
        unlimited = self.equipment_pool.filter_stratagems(by_types=[StratagemType.Defensive, StratagemType.Offensive]) or set()

        unlimited_count = 4 - (self.backpacks + self.support_weapons + self.vehicles)
        chosen_stratagems = set()
        if self.backpacks:
            if not backpacks:
                unlimited_count += 1
            else:
                bp = random.choice(list(backpacks))
                if bp in backpack_weapons:
                    self.support_weapons = 0
                chosen_stratagems.add(bp)
                self.backpacks = 0

        if self.support_weapons:
            if not support_weapons:
                unlimited_count += 1
            elif self.backpacks:
                if (sw := random.choice(list(support_weapons))) in backpack_weapons:
                    self.backpacks = 0
                chosen_stratagems.add(sw)
            else:
                chosen_stratagems.add(random.choice(list(support_weapons - backpack_weapons)))
            self.support_weapons = 0

        if self.vehicles:
            if not vehicles:
                unlimited_count += 1
            else:
                chosen_stratagems.add(random.choice(list(vehicles)))
            self.vehicles = 0

        if 1 <= (available := len(unlimited)) <= unlimited_count:
            chosen_stratagems.update(unlimited)
        elif available > unlimited_count:
            chosen_stratagems.update(random.sample(list(unlimited), k=unlimited_count))
        else:
            self.slots_defaulted.add(Slot.Stratagem)
            items, counts = DefaultDiver.randomization_counts(Slot.Stratagem)
            chosen_stratagems = random.sample(items, k=4, counts=counts)
        # noinspection bad-argument-type
        return list[Stratagem](chosen_stratagems)

    def _get_armor(self):
        mode, styles = self._armor_rule()
        op = mode.operation()
        if not (armors := op(self.equipment_pool.armor, Everything.filter_armor(styles))):
            self.slots_defaulted.add(Slot.Armor)
            items, counts = DefaultDiver.randomization_counts(Slot.Armor)
            return random.sample(items, counts=counts, k=1)
        return random.choice(armors)

    def _armor_rule(self) -> tuple[ArmorMode, set[Style]]:
        elements = Counter()
        for item, weight in self._non_armor_items():
            for style in (item.styles & Style.Elemental):
                elements[style] += weight
        if not (match := elements.most_common(1)):
            return ArmorMode.Exclude, Style.Elemental
        style, _ = match[0]
        return ArmorMode.Include, {style}


class Helldiver:
    def __init__(self, handle: str, name: str, ivd: InventoryDatabase, main_role: Style):
        self.handle = handle
        self.name = name
        self.inventory = ivd.fetch(handle)
        self.loadout_pool = self._prepare_loadout_pool(main_role)

    def _prepare_loadout_pool(self, main_role: Style):
        additional_styles = []
        all_styles = set(Style)
        base_inventory = self.inventory.filter_items(by_style=main_role)
        target_inventory = Inventory()
        target_inventory.update(base_inventory)
        while not target_inventory.ready() and all_styles:
            additional_style = random.choice(list(all_styles))
            additional_styles.append(additional_style)
            all_styles.discard(additional_style)
            target_inventory.update(ByStyle[additional_style] & base_inventory)
        return target_inventory

    def loadout(self) -> str:
        return Loadout(self.loadout_pool).format(self.name)


class RegistrationDatabase:
    def __init__(self, path: Path):
        self.path = path


class EqRandomizer:
    def __init__(self, idb: InventoryDatabase, rdb: RegistrationDatabase):
        self.inventory = idb
        self.registration = rdb

