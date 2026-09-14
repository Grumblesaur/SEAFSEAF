import operator
from collections import Counter
from enum import IntEnum

import utils
import random
from typing import TypeVar, Iterable

from inventory import (Style, Slot, EquipmentItem, Booster, Primary, Secondary, Throwable, Stratagem,
                       StratagemSubtype, StratagemType, Inventory, Everything, ByStyle, Odds)
from tracking import InventoryTracker

T = TypeVar('T')


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
        return f'__{name}__, your loadout is:\n{self}'

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
            items, counts = DefaultDive.booster_counts(used_boosters)
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
        items, counts = DefaultDive.randomization_counts(slot)
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
            items, counts = DefaultDive.randomization_counts(Slot.Stratagem)
            chosen_stratagems = random.sample(items, k=4, counts=counts)
        # noinspection bad-argument-type
        return list[Stratagem](chosen_stratagems)

    def _get_armor(self):
        mode, styles = self._armor_rule()
        op = mode.operation()
        if not (armors := op(self.equipment_pool.armor, Everything.filter_armor(styles))):
            self.slots_defaulted.add(Slot.Armor)
            items, counts = DefaultDive.randomization_counts(Slot.Armor)
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

    def __init__(self, handles_to_names: dict[str, str], idb: InventoryTracker):
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
            loadout_strings.append(f'-#{Loadout.WarningSymbol} No items available for slot type.'
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


class Playstyle:
    Headers = ['Your focus is on', 'You specialize in', 'Your work entails',
               'Bring a kit designed around', 'Your duties involve']
    Signoff = ['May the light of Libery guide you.',
               'Let no opponent go unhindered by the corpses of their comrades.',
               'Super Earth is counting on you.',
               'Clear a path for Democracy.']

    def __init__(self, names: list[str]):
        self.helldivers = dict(zip(names, random.sample(Style, k=(n := len(names)))))
        self.signoff = random.choice(self.Signoff)
        self.headers = dict(zip(names, random.sample(self.Headers, k=n)))

    def __str__(self) -> str:
        plural = len(self.helldivers) > 1
        lines = [f'Helldiver{"s" if plural else ""}! Here is your assignment:']
        for name, role in self.helldivers.items():
            lines.append(f'- __{name}__, you are our **{role.name}**. {self.headers[name]} {role.value}.')
        lines.append(self.signoff)
        return '\n'.join(lines)


class DefaultDive:
    Loadout = {
        Slot.Armor: {
            Everything.lookup('B-01'): Odds.Common,
            Everything.lookup('TR-40'): Odds.Rare,
            Everything.lookup('TR-7'): Odds.Rare,
        },
        Slot.Primary: {
            Everything.lookup('AR-23'): Odds.Common,
            Everything.lookup('R-2124'): Odds.Rare,
        },
        Slot.Secondary: {
            Everything.lookup('P-2'): Odds.Common,
            Everything.lookup('P-19'): Odds.Special,
            Everything.lookup('P-4'): Odds.Special,
            Everything.lookup('P-113'): Odds.Special,
            Everything.lookup('GP-31'): Odds.Special,
        },
        Slot.Throwable: {
            Everything.lookup('G-12'): Odds.Common,
            Everything.lookup('G-6'): Odds.Special,
            Everything.lookup('G-16'): Odds.Rare,
        },
        Slot.Stratagem: {
            Everything.lookup(by_name='Eagle Airstrike'): Odds.Common,
            Everything.lookup(by_name='Eagle Strafing Run'): Odds.Common,
            Everything.lookup(by_name='Eagle 500kg Bomb'): Odds.Rare,
            Everything.lookup(by_name='Orbital Precision Strike'): Odds.Common,
            Everything.lookup(by_name='Orbital Gatling Barrage'): Odds.Special,
            Everything.lookup('MG-43'): Odds.Common,
            Everything.lookup('M-105'): Odds.Special,
            Everything.lookup('EAT-17'): Odds.Common,
            Everything.lookup('GR-8'): Odds.Rare,
            Everything.lookup('MG-206'): Odds.Rare,
            Everything.lookup('B-1'): Odds.Common,
            Everything.lookup('AX/AR-23'): Odds.Common,
            Everything.lookup('A/MG-43'): Odds.Common,
            Everything.lookup('A/G-16'): Odds.Special,
        },
        Slot.Booster: {
            Everything.lookup(by_name='Vitality Enhancement'): Odds.Common,
            Everything.lookup(by_name='Hellpod Space Optimization'): Odds.Common,
            Everything.lookup(by_name='Stamina Enhancement'): Odds.Special,
            Everything.lookup(by_name='UAV Recon Booster'): Odds.Rare,
            Everything.lookup(by_name='Muscle Enhancement'): Odds.Rare,
            Everything.lookup(by_name='Increased Reinforcement Budget'): Odds.Rare,
        }
    }

    def __init__(self, names: list[str]):
        self.players = {name: {} for name in names}
        used_boosters = set()
        for player in self.players:
            boosters, bcounts = self.booster_counts(used_boosters)
            b = random.sample(boosters, counts=bcounts, k=1)
            used_boosters.add(b[0])
            self.players[player][Slot.Booster] = b

        for slot in [Slot.Throwable, Slot.Primary, Slot.Secondary, Slot.Armor]:
            for player in self.players:
                items, counts = self.randomization_counts(slot)
                x = random.sample(items, counts=counts, k=1)
                self.players[player][slot] = x

        for player in self.players:
            stratagems, scounts = self.randomization_counts(Slot.Stratagem)
            strats = random.sample(stratagems, counts=scounts, k=4)
            self.players[player][Slot.Stratagem] = strats

    def __str__(self) -> str:
        parts = []
        for player, equipment in self.players.items():
            lines = [f'__{player}__, your loadout is:']
            for slot, contents in sorted(equipment.items(), key=lambda p: p[1].sort_key()):
                lines.append(f'**{slot.name}**: {utils.format_series(contents)}')
            parts.append('\n'.join(lines))
        return '\n\n'.join(parts)

    @classmethod
    def randomization_counts(cls, slot: Slot) -> tuple[list[EquipmentItem], list[int]]:
        items, counts = [], []
        for item, odds in cls.Loadout[slot].items():
            items.append(item)
            counts.append(int(odds))
        return items, counts

    @classmethod
    def booster_counts(cls, used_boosters) -> tuple[list[Booster], list[int]]:
        slot_copy = {eitem: odds for eitem, odds in cls.Loadout[Slot.Booster]}
        for ub in used_boosters:
            slot_copy.pop(ub, None)
        items, counts = [], []
        for item, odds in slot_copy.items():
            items.append(item)
            counts.append(int(odds))
        return items, counts
