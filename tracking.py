import datetime
import os
from enum import StrEnum
from pathlib import Path

import utils
from inventory import Inventory, Everything, Source
from utils import prefix_match


class RegistrationMode(StrEnum):
    Clear = 'Unregister'
    Drop = 'Delete'
    Set = 'Replace'
    Add = 'Include'

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
                self.registered.discard(handle)
                self.user_path(handle).unlink(missing_ok=True)
                return "Your inventory has been erased."
            case RegistrationMode.Add:
                if handle in self.registered:
                    inventory = self.fetch(handle)
                    inventory += Everything.make_subset(sources, designations, names)
                else:
                    inventory = Everything.make_subset(self.DefaultSources, designations, names)
                verb = 'now includes'
            case RegistrationMode.Set:
                inventory = Everything.make_subset(sources, designations, names)
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

