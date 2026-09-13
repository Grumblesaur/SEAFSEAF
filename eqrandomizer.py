import operator
import os
from collections import Counter
import datetime
from enum import IntEnum
from pathlib import Path

import utils
from inventory import Inventory, Everything, DefaultDiver, ByStyle
import random
from equipment import Style, Slot, EquipmentItem, Booster, StratagemSubtype, StratagemType, Primary, Secondary, \
    Throwable, Stratagem, Source
from typing import TypeVar, Iterable

T = TypeVar('T')


class RegistrationMode(IntEnum):
    Delete = -1
    Replace = 0
    Add = 1


class InventoryDatabase:
    DefaultSources = {Source.Stock, Source.HM, Source.PAC, Source.HG,
                      Source.EB, Source.BR, Source.OC, Source.RW}
    def __init__(self, path: Path):
        self.path = path
        self.registered = set()
        for filename in os.listdir(self.path):
            file = Path(filename)
            self.registered.add(file.name.removesuffix(file.suffix))
        self.cache = dict[str, Inventory]()
        self.last_time_used = dict[str, datetime.datetime]()

    def __contains__(self, handle: str) -> bool:
        return handle in self.registered

    def user_path(self, handle: str) -> Path:
        return self.path / f'{handle}.txt'

    def fetch(self, handle: str) -> Inventory:
        self.touch(handle)
        if not (path := self.user_path(handle)).exists():
            self.register(handle, self.DefaultSources, rmode=RegistrationMode.Replace)
        if (cached := self.cache.get(handle)) is not None:
            return cached
        with open(path, 'r', encoding='utf-8') as f:
            cachable = eval(f.read())
        self.touch(handle, cachable)
        return cachable

    def touch(self, handle: str, inventory: Inventory | None = None):
        self.last_time_used[handle] = datetime.datetime.now()
        if inventory is not None:
            self.cache[handle] = inventory
            with open(self.user_path(handle), 'w', encoding='utf-8') as f:
                f.write(repr(inventory) + '\n')


    def register(self, handle: str,
                 sources: set[Source] | None = None,
                 designations: set[Source] | None = None,
                 names: set[Source] | None = None,
                 rmode: RegistrationMode = RegistrationMode.Add):
        match rmode:
            case RegistrationMode.Delete:
                self.registered.discard(handle)
                self.user_path(handle).unlink(missing_ok=True)
                return
            case RegistrationMode.Add:
                if handle in self.registered:
                    inventory = self.fetch(handle)
                    inventory += Everything.make_subset(sources, designations, names)
                else:
                    inventory = Everything.make_subset(self.DefaultSources, designations, names)
            case RegistrationMode.Replace:
                inventory = Everything.make_subset(sources, designations, names)
        self.touch(handle, inventory)


class ArmorMode(IntEnum):
    Include = 1
    Exclude = 0

    def operation(self):
        if self is self.Include:
            return operator.and_
        return operator.sub


class Loadout:
    VehicleRoles = {Style.Driver, Style.Pilot}
    ElementalThreshold = 3
    WarningSymbol = ' [!]'
    def __init__(self, loadout_pool: Inventory, role: Style, vehicles: int = 1, backpacks: int = 1, support_weapons: int = 1,
                 used_boosters: set[Booster] | None = None):
        used_boosters = used_boosters or set()
        self.vehicles = vehicles if role not in self.VehicleRoles else 1
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

    def warning(self, slot: Slot):
        return self.WarningSymbol if slot in self.slots_defaulted else ''

    def __str__(self):
        stratagems = [str(s) for s in self.stratagem]
        return'\n'.join([
            f'- **Primary{self.warning(Slot.Primary)}:** `{self.primary}`',
            f'- **Secondary{self.warning(Slot.Secondary)}:** `{self.secondary}`',
            f'- **Throwable{self.warning(Slot.Throwable)}:** `{self.throwable}`',
            f'- **Stratagem{self.warning(Slot.Stratagem)}:** {utils.format_series(stratagems)}',
            f'- **Booster{self.warning(Slot.Booster)}:** `{self.booster}`',
            f'- **Armor**{self.warning(Slot.Armor)}:** `{self.armor}`',
        ])

    def _non_armor_items(self) -> Iterable[tuple[EquipmentItem, int]]:
        yield self.primary, 3
        yield self.secondary, 2
        yield self.throwable, 1
        for strat in self.stratagem:
            yield strat, 2
        yield self.booster, 1

    def _get_booster(self, used_boosters: set[Booster]) -> Booster:
        if not (boosters := self.equipment_pool.booster - used_boosters):
            items, counts = DefaultDiver.booster_counts(used_boosters)
            booster = random.sample(items, counts=counts, k=1)[0]
        else:
            booster = random.choice(list(boosters))
        used_boosters.add(booster)
        return booster


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


def split(n: int, squad_size: int) -> list[int]:
    filled = [1 for _ in range(n)]
    padding = [0] * (squad_size - len(filled))
    whole = filled + padding
    random.shuffle(whole)
    return whole

class Squad:
    @staticmethod
    def supply_limits_kwargs(squad_size: int) -> list[dict[str, int]]:
        veh_dist = [0, 0, 0, 0, 0, 1, 1, 1]
        sup_dist = [0, 1, 1, 1]
        bac_dist = [0, 1]
        if squad_size > 1:
            sup_dist.append(2)
        if squad_size > 2:
            bac_dist.append(2)
            sup_dist.append(3)
            sup_dist.remove(0)
        if squad_size > 3:
            veh_dist.append(2)
            veh_dist.remove(1)
            sup_dist.remove(0)
            bac_dist.remove(0)

        backpacks = random.choice(bac_dist)
        vehicles = random.choice(veh_dist)
        support_weapons = random.choice(sup_dist)
        return [{'backpacks': b, 'vehicles': v, 'support_weapons': s}
                for b, v, s in zip(split(backpacks, squad_size),
                                   split(vehicles, squad_size),
                                   split(support_weapons, squad_size))]

    def __init__(self, handles_to_names: dict[str, str], idb: InventoryDatabase):
        self.handles_to_names = handles_to_names
        loadout_pools = {}
        roles = {}
        for handle, role in zip(handles_to_names.keys(), random.sample(list(Style), k=len(self.handles_to_names))):
            loadout_pools[handle] = self._prepare_loadout_pool(idb.fetch(handle), role)
            roles[handle] = role

        self.loadouts = dict[str, Loadout]()
        used_boosters = set()
        kwargs_groups = self.supply_limits_kwargs(len(handles_to_names))
        for handle, lp in loadout_pools.items():
            kwargs = kwargs_groups.pop()
            lo = Loadout(lp, roles[handle], **kwargs, used_boosters=used_boosters)
            self.loadouts[handle] = lo

    def __str__(self):
        loadout_strings = [loadout.format(self.handles_to_names[handle]) for handle, loadout in self.loadouts.items()]
        if any(lo.slots_defaulted for lo in self.loadouts.values()):
            loadout_strings.append(f'-#{Loadout.WarningSymbol} Insufficient items available for slot type.'
                                   ' Slot filled with default diving equipment.')
        return '\n\n'.join(loadout_strings)

    @staticmethod
    def _prepare_loadout_pool(inv: Inventory, main_role: Style):
        additional_styles = []
        remaining_styles = set(Style) - {main_role}
        base_inventory = inv.filter_items(by_style=main_role)
        target_inventory = Inventory()
        target_inventory.update(base_inventory)
        while not target_inventory.ready() and remaining_styles:
            additional_style = random.choice(list(remaining_styles))
            additional_styles.append(additional_style)
            remaining_styles.discard(additional_style)
            target_inventory.update(ByStyle[additional_style] & base_inventory)
        return target_inventory


class Piecemeal:
    def __init__(self, inv: Inventory, slots: set[Slot]):
        self.selections = {}
        for slot in slots:
            if options := inv.slot(slot):
                self.selections[slot] = random.sample(list(options), k=slot.required())
            else:
                self.selections[slot] = f'<no equipment registered for {slot} slot>'

    def __str__(self):
        parts = ['You have been assigned equipment in the following slots:']
        for slot, selection in sorted(self.selections.items(), key=lambda p: p[0].sort_key()):
            parts.append(f'**{slot.name}**: {utils.format_series(selection)}')
        return '\n'.join(parts)


