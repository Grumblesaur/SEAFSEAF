import random
from collections import defaultdict
from typing import Iterable

import utils
from exceptions import InvalidSquad
from registration import PlayerRegistry, EquipmentCatalog, PrimaryType, SecondaryType, ThrowableType, StratagemType, \
    StratagemSubtype, ArmorWeight
from utils import format_series


def roll_against_odds(numerator: int, denominator: int) -> bool:
    return random.randint(1, denominator) <= numerator

class DifficultyOrder:
    Levels = {
        0: "Helldiver's Choice",
        1: 'Trivial',
        2: 'Easy',
        3: 'Medium',
        4: 'Challenging',
        5: 'Hard',
        6: 'Extreme',
        7: 'Suicide Mission',
        8: 'Impossible',
        9: 'Helldive',
        10: 'Super Helldive',
    }

    def postamble(self):
        if self.level == 0:
            return random.choice(["Don't disappoint us.", "Show the galaxy what Super Earth is made of."])
        if self.level in range(1, 4):
            return random.choice(["Don't screw this up.", "It should be a worthy warm-up for one of your caliber."])
        if self.level in range(4, 8):
            return random.choice(["Good luck out there.", "We're counting on you."])
        return random.choice(["Super Earth thanks you for your heroism.", "The shining glory of Democracy awaits you."])

    Distribution = [1,
                    2,
                    3,
                    4, 4,
                    5, 5, 5,
                    6, 6, 6, 6,
                    7, 7, 7, 7, 7,
                    8, 8, 8, 8, 8, 8, 8, 8, 8,
                    9, 9, 9, 9, 9, 9, 9, 9,
                    10, 10, 10, 10, 10, 10,
                    0]

    def __init__(self, *args, **kwargs):
        self.level = random.choice(self.Distribution)

    def __str__(self):
        name = self.Levels[self.level]
        return f'Helldiver! You have been assigned to fight at level {self.level}: {name}. {self.postamble()}'



class FactionOrder:
    Factions = {
        'Terminids': ['Rupture Strain', 'Spore Burst', 'Predator Strain'],
        'Automatons': ['Jet Brigade', 'Incineration Corps', 'Cyborg Legion'],
        'Illuminate': ['Mindless Masses', 'Appropriators', 'Vote Snatchers'],
    }
    Verbs = ['squash', 'crush', 'smash', 'exterminate', 'destroy', 'obliterate',
             'spread the light of democracy to', 'eliminate', 'annihilate']

    Nouns = ['hammer', 'fist', 'might', 'glory', 'fury', 'righteousness', 'pride',
             'zeal', 'fervor']

    SubfactionOdds = (3, 20)

    def __init__(self, *args, **kwargs):
        self.faction = random.choice(list(self.Factions.keys()))
        if roll_against_odds(*self.SubfactionOdds):
            self.subfaction = random.choice(self.Factions[self.faction])
        else:
            self.subfaction = ""
        self.verb = random.choice(self.Verbs)
        self.noun = random.choice(self.Nouns)

    def __str__(self):
        target = self.subfaction if self.subfaction else self.faction
        mission = (f"Helldiver! You must seek out the {target} and {self.verb} them"
                   + f" with the {self.noun} of Super Earth. ")
        if self.subfaction:
            mission += (f"If there are no {self.subfaction} incursions to be found,"
                        f" target any other {self.faction} as you see fit.")
        return mission


class PlanetOrder:
    BiomeArchetypes = {
        'Sandy': ['Desert Dunes', 'Desert Cliffs', 'Acidic Badlands', 'Rocky Canyons', 'Moon'],
        'Primordial': ['Volcanic Jungle', 'Deadlands', 'Ethereal Jungle', 'Ionic Jungle'],
        'Arctic': ['Icy Glaciers', 'Boneyard'],
        'Moor': ['Plains', 'Tundra', 'Scorched Moor', 'Ionic Crimson'],
        'Swamp': ['Basic Swamp', 'Haunted Swamp'],
        'Forest': ['Deciduous Forest', 'Autumn Forest', 'Crimson Forest'],
    }
    ConditionsByBiome = {
        'Desert Dunes': ['Intense Heat', 'Extreme Cold', 'Sandstorms'],
        'Desert Cliffs': ['Intense Heat', 'Tremors'],
        'Acidic Badlands': ['Acid Storms'],
        'Moon': ['Extreme Cold', 'Meteor Storms'],
        'Rocky Canyons': ['Tremors'],
        'Deadlands': ['Thick Fog'],
        'Ethereal Jungle': [],
        'Ionic Jungle': ['Ion Storms'],
        'Volcanic Jungle': ['Rainstorms', 'Volcanic Activity'],
        'Boneyard': ['Extreme Cold'],
        'Icy Glaciers': ['Blizzards', 'Extreme Cold'],
        'Ionic Crimson': ['Ion Storms'],
        'Plains': ['Rainstorms'],
        'ScorchedMoor': ['Intense Heat', 'Fire Tornadoes'],
        'Tundra': [None],
        'Basic Swamp': ['Rainstorms'],
        'Haunted Swamp': ['Thick Fog'],
        'Autumn Forest': [None],
        'Deciduous Forest': [None],
    }

    Preambles = [
        "Super Earth High Command requires performance data for your equipment",
        "Super Earth researchers have made a data request for operations",
        "Super Earth scientists need real-world data for their new hypothesis about combat",
        "Super Earth engineers need to know how your weapons stand up",
    ]

    def __init__(self, *args, **kwargs):
        order_types = ['Planet', 'Biome', 'Condition']
        preamble = random.choice(self.Preambles)
        if (order_type := random.choice(order_types)) == 'Planet':
            planet = random.choice(list(self.BiomeArchetypes.keys()))
            message = (f"Helldiver! {preamble} on {planet.lower()}-type planets. Consider"
                       f" this when plotting your super destroyer's next course.")
        elif order_type == 'Biome':
            biomes = random.choices(list(self.ConditionsByBiome.keys()), k=2)
            message = (f"Helldiver! {preamble} in the conditions of {biomes[0].lower()} and"
                       f" {biomes[1].lower()} biomes. Prioritize such worlds"
                       f" during your super destroyer's next war council.")
        else:  # 'Condition'
            biomes = random.choices(list(self.ConditionsByBiome.keys()), k=3)
            conditions = set()
            for biome in biomes:
                for condition in self.ConditionsByBiome[biome]:
                    conditions.add(condition)
            selected = list({c for c in random.choices(list(conditions), k=2) if c is not None})
            message = "Helldiver! "
            if len(selected) == 0:
                message += (f'{preamble} under ordinary conditions. Avoid operational areas'
                            f' with environmental hazards for your next deployment!')
            elif len(selected) == 1:
                message += (f'{preamble} under conditions of {selected[0].lower()}.'
                            ' Prioritize operational areas with this condition for your'
                            ' next deployment!')
            else:
                message = (f"Helldiver! {preamble} under conditions of {selected[0].lower()}"
                           f" and {selected[1].lower()}. Prioritize areas with one of these conditions"
                           f" for your next deployment!")
        self.message = message

    def __str__(self):
        return self.message


class EquipmentOrder:
    Preambles = {
        "Your super destroyer has been selected by High Command to demonstrate the": "and",
        "You must confirm your training certification with the": "or",
        "General Brasch has ordered a fleet-wide exercise requiring the use of the": "or",
    }

    Postambles = [
        "Please ensure your compliance with this order.",
        "Do not tarry! Take action immediately!",
        "Show the galaxy your skill."
    ]
    def __init__(self, equipment_items: Iterable[str]):
        self.equipment = sorted(equipment_items)

    def __str__(self):
        preamble, conj = random.choice(list(self.Preambles.items()))
        postamble = random.choice(self.Postambles)
        return ' '.join([
            'Helldiver!',
            f'{preamble} {format_series(self.equipment, conjunction=conj)}.',
            postamble,
            "\nIf you have not been authorized to the listed item(s), use your best judgement in selecting"
            " a substitute."
        ])


class Helldiver:
    def __init__(self, user_handle: str, player_registry: PlayerRegistry):
        self.equipment = player_registry.fetch_equipment(user_handle)
        self.primary: str | None = None
        self.secondary: str | None = None
        self.throwable: str | None = None
        self.stratagems: list[str] = []
        self.booster: str | None = None
        self.armor: str | None = None
        self.loadout_set = False


    def make_loadout(self, catalog: EquipmentCatalog, support_weapons: int = 1, backpacks: int = 1, vehicles: int = 1,
                     used_boosters: set[str] | None = None, used_supply: set[str] | None = None):
        used_boosters = used_boosters or set()
        used_supply = used_supply or set()
        if len(available_stratagems := self.equipment['Stratagems'] & catalog.stratagems['all']) <= 4:
            self.stratagems = list(available_stratagems) or ["<no stratagems registered>"]
        else:
            unrestricted_stratagems = catalog.stratagems['types']['Offensive'] | catalog.stratagems['types']['Defensive']
            unrestricted_available = self.equipment['Stratagems'] & unrestricted_stratagems
            vehicle_stratagems = catalog.stratagems['types']['Vehicle']
            vehicles_available = self.equipment['Stratagems'] & vehicle_stratagems
            plain_support_weapons = catalog.stratagems['subtypes']['Weapon']
            plain_support_weapons_available = (self.equipment['Stratagems'] & plain_support_weapons) - used_supply
            backpack_stratagems = (catalog.stratagems['subtypes']['Backpack']
                                   | (backpack_weapons := catalog.stratagems['subtypes']['BackpackWeapon']))
            backpacks_available = (self.equipment['Stratagems'] & backpack_stratagems) - used_supply
            support_weapon_open = True
            if vehicles and vehicles_available and random.choice((False, False, True)):
                self.stratagems.append(random.choice(list(vehicles_available)))
            if backpacks and backpacks_available and random.choice((False, False, True)):
                self.stratagems.append(backpack := random.choice(list(backpacks_available)))
                if backpack in backpack_weapons:
                    support_weapon_open = False
            if support_weapons and support_weapon_open:
                self.stratagems.append(random.choice(list(plain_support_weapons_available)))
            self.stratagems.extend(random.sample(list(unrestricted_available), k=4-len(self.stratagems)))

        self.primary = random.choice(list(self.equipment['Primary']) or ["<no primaries registered>"])
        self.secondary = random.choice(list(self.equipment['Secondary']) or ["<no secondaries registered>"])
        self.throwable = random.choice(list(self.equipment['Throwable']) or ["<no throwables registered>"])
        self.booster = random.choice(list(self.equipment['Booster'] - used_boosters) or ["<no boosters registered>"])
        self.armor = random.choice(list(self.equipment['Armor']) or ["<no armor registered>"])
        self.loadout_set = True


    def __str__(self):
        layout = [f'- **Primary:** `{self.primary}`',
                  f'- **Secondary:** `{self.secondary}`',
                  f'- **Throwable:** `{self.throwable}`',
                  f'- **Stratagems:** {utils.format_series(self.stratagems)}',
                  f'- **Booster:** `{self.booster}`',
                  f'- **Armor:** `{self.armor}`']
        return '\n'.join(layout)


def calculate_squad_limits(squad_size: int) -> dict[str, int]:
    if 2 > squad_size > 4:
        raise InvalidSquad(f"Squad must have exactly 2, 3, or 4 members, not {squad_size}.")
    if squad_size == 2:
        vehicles = random.randint(0, 1)
        backpacks = random.randint(0, 1)
        support_weapons = random.randint(1-backpacks, 2-backpacks)
    elif squad_size == 3:
        vehicles = random.randint(0, 2)
        backpacks = random.randint(0, 2)
        support_weapons = random.randint(2-backpacks, 3-backpacks)
    else:
        vehicles = random.randint(0, 2)
        backpacks = random.randint(0, 3)
        support_weapons = random.randint(3-backpacks, 4-backpacks)
    return {'vehicles': vehicles, 'backpacks': backpacks, 'support_weapons': support_weapons}

def split(cap: int, squad_size: int) -> list[int]:
    v = [1 for _ in range(cap)]
    v.extend([0 for _ in range(squad_size - cap)])
    random.shuffle(v)
    return v


class Randomizer:
    def __init__(self, player_registry: PlayerRegistry, equipment_catalog: EquipmentCatalog):
        self.registry = player_registry
        self.catalog = equipment_catalog

    def primary(self, by_type: PrimaryType | None = None, n: int = 1) -> str:
        if by_type is None:
            primaries = self.catalog.primaries['all']
        else:
            primaries = self.catalog.primaries['types'][by_type.value]
        eqo = EquipmentOrder(random.sample(list(primaries), k=n))
        return str(eqo)

    def secondary(self, by_type: SecondaryType | None = None, n: int = 1) -> str:
        if by_type is None:
            secondaries = self.catalog.secondaries['all']
        else:
            secondaries = self.catalog.secondaries['types'][by_type.value]
        eqo = EquipmentOrder(random.sample(list(secondaries), k=n))
        return str(eqo)

    def throwable(self, by_type: ThrowableType | None = None, n: int = 1) -> str:
        if by_type is None:
            throwables = self.catalog.throwable['all']
        else:
            throwables = self.catalog.throwable['types'][by_type.value]
        eqo = EquipmentOrder(random.sample(list(throwables), k=n))
        return str(eqo)

    def stratagems(self, by_type: StratagemType | None = None, by_subtype: StratagemSubtype | None = None, n: int = 1) -> str:
        if by_type is not None and by_subtype is not None:
            by_type.validate_subtype(by_subtype)
            stratagems_by_subtype = self.catalog.stratagems['subtypes'][by_subtype.name]
            stratagems_by_type = self.catalog.stratagems['types'][by_type.name]
            stratagems = stratagems_by_subtype & stratagems_by_type
        elif by_type is not None and by_subtype is None:
            stratagems = self.catalog.stratagems['types'][by_type.name]
        elif by_type is None and by_subtype is not None:
            stratagems = self.catalog.stratagems['subtypes'][by_subtype.name]
        else:
            stratagems = self.catalog.stratagems['all']
        eqo = EquipmentOrder(random.sample(list(stratagems), k=n))
        return str(eqo)

    def booster(self, n: int = 1) -> str:
        eqo = EquipmentOrder(random.sample(list(self.catalog.boosters['all']), k=n))
        return str(eqo)

    def armor(self, by_weight: ArmorWeight | None = None, n: int = 1) -> str:
        if by_weight is None:
            armors = self.catalog.armor['all']
        else:
            armors = self.catalog.armor['weights'][by_weight.name]
        eqo = EquipmentOrder(random.sample(list(armors), k=n))
        return str(eqo)

    @staticmethod
    def faction_order(*args, **kwargs) -> str:
        return str(FactionOrder(*args, **kwargs))

    @staticmethod
    def difficulty_order(*args, **kwargs) -> str:
        return str(DifficultyOrder(*args, **kwargs))

    @staticmethod
    def planet_order(*args, **kwargs) -> str:
        return str(PlanetOrder(*args, **kwargs))

    @staticmethod
    def mission(*args, **kwargs) -> str:
        mission_type = random.choice([
            FactionOrder, DifficultyOrder, PlanetOrder
        ])
        return str(mission_type())

    def solo_loadout(self, user_handle: str) -> dict[str, str]:
        helldiver = Helldiver(user_handle, self.registry)
        helldiver.make_loadout(self.catalog)
        return {user_handle: str(helldiver)}

    def squad_loadout(self, user_handles: list[str]) -> dict[str, str]:
        limits = calculate_squad_limits(squad_size := len(user_handles))
        random.shuffle(user_handles)
        user_args = defaultdict(dict)
        for key, value in limits.items():
            for user_handle, limit in zip(user_handles, split(value, squad_size)):
                user_args[user_handle][key] = limit

        loop_items = sorted(((handle, Helldiver(handle, self.registry), kwargs)
                            for handle, kwargs in user_args.items()),
                            key=lambda t: len(t[1].equipment['boosters']))

        loadouts = {}
        accumulated_boosters = set()
        accumulated_supply = set()

        for handle, helldiver, kwargs in loop_items:
            helldiver.make_loadout(self.catalog,
                                   **kwargs,
                                   used_boosters=accumulated_boosters,
                                   used_supply=accumulated_supply)
            accumulated_boosters.add(helldiver.booster)
            accumulated_supply.update(set(helldiver.stratagems)
                                      & self.catalog.stratagems['types']["Supply"])
            loadouts[handle] = str(helldiver)
        return loadouts


