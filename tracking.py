import datetime
import os
import threading
import time
from enum import StrEnum
from pathlib import Path
from typing import NoReturn

import utils
from inventory import Inventory, Everything, Source, Style, Slot
# noinspection unused-imports
#  - required for eval()
from inventory import Primary, Secondary, Booster, Stratagem, Armor, Throwable
# noinspection unused-imports
#  - required for eval()
from inventory import PrimaryType, SecondaryType, StratagemType, StratagemSubtype, Weight, Passive, ThrowableType
from utils import prefix_match


class RegistrationMode(StrEnum):
    Clear = 'Unregister'
    Drop = 'Delete'
    Set = 'Replace'
    Add = 'Include'

    def sentence(self):
        h = 'Select sources'
        match self:
            case self.Add:
                return f'{h} to add items to your inventory.'
            case self.Set:
                return f'{h} to change your inventory.'
            case self.Drop:
                return f'{h} to remove items from your inventory.'
            case self.Clear:
                return 'All items will be removed from your inventory.'


    @classmethod
    def from_string(cls, s: str) -> RegistrationMode:
        cf = s.casefold()
        for ev in cls:
            if prefix_match(ev, cf):
                return ev
        return cls.Clear


class InventoryTracker:
    DefaultSources = {Source.STOCK, Source.HM, Source.PAC, Source.HG,
                      Source.EB, Source.BR, Source.OC, Source.RW}
    def __init__(self, path: Path, prune_period_seconds: int = 2 * 60 * 60):
        self.path = path
        self.registered = set()
        for filename in os.listdir(self.path):
            file = Path(filename)
            self.registered.add(file.name.removesuffix(file.suffix))
        self.cache = dict[str, Inventory]()
        self.last_time_used = dict[str, datetime.datetime]()
        self.pruning_period = prune_period_seconds

        def pruning_task(inventory_tracker: InventoryTracker) -> NoReturn:
            while True:
                time.sleep(inventory_tracker.pruning_period)
                pruned = inventory_tracker.prune()
                print(f'pruned {pruned} objects from cache.')

        self.pruner = threading.Thread(target=pruning_task, args=(self,), daemon=True)
        self.pruner.start()
        print(f'Self-pruning thread initialized. Culling cycle: {prune_period_seconds / 3600:.2f} hour(s).')

    def prune(self):
        prune_candidates = set()
        now = datetime.datetime.now()
        for handle, last_time_used in self.last_time_used.items():
            if (now - last_time_used) >= datetime.timedelta(seconds=self.pruning_period):
                prune_candidates.add(handle)
        for pc in prune_candidates:
            self.cache.pop(pc, None)
            self.last_time_used.pop(pc, None)
        return len(prune_candidates)

    def __contains__(self, handle: str) -> bool:
        return handle in self.registered

    def user_path(self, handle: str) -> Path:
        return self.path / f'{handle}.txt'

    def fetch(self, handle: str) -> Inventory:
        self.touch(handle)
        if not (path := self.user_path(handle)).exists():
            self.register(handle, self.DefaultSources, rmode=RegistrationMode.Set)
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
                 rmode: RegistrationMode = RegistrationMode.Add) -> str:
        match rmode:
            case RegistrationMode.Clear:
                if handle in self:
                    adverb = ' '
                    self.registered.discard(handle)
                else:
                    adverb = ' already '
                self.user_path(handle).unlink(missing_ok=True)
                return f"Your inventory has{adverb}been erased."
            case RegistrationMode.Add:
                if handle in self.registered:
                    inventory = self.fetch(handle)
                    inventory += Everything.make_subset(sources, designations, names)
                else:
                    self.registered.add(handle)
                    inventory = Everything.make_subset(self.DefaultSources, designations, names)
                verb = 'now includes'
            case RegistrationMode.Set:
                inventory = Everything.make_subset(sources, designations, names)
                self.registered.add(handle)
                verb = 'is now set to'
            case RegistrationMode.Drop:
                inventory = self.fetch(handle)
                dropping = inventory.make_subset(sources, designations, names)
                inventory -= dropping
                verb = 'now lacks'
        self.touch(handle, inventory)

        parts = [f'Your inventory {verb}']
        individual = list(names) if names is not None else []
        individual.extend(designations or [])
        items = utils.format_series(individual) if individual else ''
        groups = utils.format_series(sources) if sources else ''

        if items and groups:
            parts.append(f'{items}; as well as all items from {groups}.')
        elif items:
            parts.append(f'{items}.')
        else:
            parts.append(f'{groups}.')
        return ' '.join(parts)

