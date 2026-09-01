import random
from typing import Iterable

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
    Distribution = [1,
                    2,
                    3,
                    4, 4,
                    5, 5,
                    6, 6, 6,
                    7, 7, 7, 7, 7,
                    8, 8, 8, 8, 8, 8, 8, 8,
                    9, 9, 9, 9, 9, 9, 9,
                    10, 10, 10, 10,
                    0, 0, 0, 0, 0, 0]

    def __init__(self, *args, **kwargs):
        self.level = random.choice(self.Distribution)

    def __str__(self):
        return self.Levels[self.level]



class FactionOrder:
    Factions = {
        'Terminids': ['Rupture Strain', 'Spore Burst', 'Predator Strain'],
        'Automatons': ['Jet Brigade', 'Incineration Corps', 'Cyborg Legion'],
        'Illuminate': ['Mindless Masses', 'Appropriators'],
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
        mission = (f"Helldivers! You must seek out the {target} and {self.verb} them"
                   + f"with the {self.noun} of Super Earth. ")
        if self.subfaction:
            mission += (f"If there are no {self.subfaction} incursions to be found, "
                        f"target any other {self.faction} as you see fit.")
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
        "Super Earth scientists have a new hypothesis about combat",
        "Super Earth engineers need to know how your weapons stand up",
    ]

    def __init__(self, *args, **kwargs):
        order_types = ['Planet', 'Biome', 'Condition']
        preamble = random.choice(self.Preambles)
        if (order_type := random.choice(order_types)) == 'Planet':
            planet = random.choice(list(self.BiomeArchetypes.keys()))
            message = (f"Helldivers! {preamble} on a {planet.lower()} planet. Consider"
                       f" this when plotting your super destroyer's next course.")
        elif order_type == 'Biome':
            biomes = random.choices(list(self.ConditionsByBiome.keys()), k=2)
            message = (f"Helldivers! {preamble} in the conditions of {biomes[0].lower()} and"
                       f" {biomes[1].lower()} biomes. Prioritize such worlds "
                       f" during your super destroyer's next war council.")
        else:  # 'Condition'
            biomes = random.choices(list(self.ConditionsByBiome.keys()), k=3)
            conditions = set()
            for biome in biomes:
                for condition in self.ConditionsByBiome[biome]:
                    conditions.add(condition)
            selected = [c for c in random.choices(list(conditions), k=2) if c is not None]
            message = "Helldivers! "
            if len(selected) == 0:
                message += (f'{preamble} under ordinary conditions. Avoid operational areas'
                            f' with environmental hazards for your next deployment!')
            elif len(selected) == 1:
                message += (f'{preamble} under conditions of {selected[0].lower()}.'
                            ' Prioritize operational areas with this condition for your'
                            ' next deployment!')
            else:
                message = (f"Helldivers! {preamble} under conditions of {selected[0].lower()}"
                           f" and {selected[0].lower()}. Prioritize areas with one of these conditions"
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



class Randomizer:
    def __init__(self, player_registry: PlayerRegistry, equipment_catalog: EquipmentCatalog):
        self.registry = player_registry
        self.catalog = equipment_catalog

    def primary(self, by_type: PrimaryType | None = None, n: int = 1):
        if by_type is None:
            primaries = self.catalog.primaries['all']
        else:
            primaries = self.catalog.primaries['types'][by_type.value]
        eqo = EquipmentOrder(random.sample(list(primaries), k=n))
        return str(eqo)

    def secondary(self, by_type: SecondaryType | None = None, n: int = 1):
        if by_type is None:
            secondaries = self.catalog.secondaries['all']
        else:
            secondaries = self.catalog.secondaries['types'][by_type.value]
        eqo = EquipmentOrder(random.sample(list(secondaries), k=n))
        return str(eqo)

    def throwable(self, by_type: ThrowableType | None = None, n: int = 1):
        if by_type is None:
            throwables = self.catalog.throwable['all']
        else:
            throwables = self.catalog.throwable['types'][by_type.value]
        eqo = EquipmentOrder(random.sample(list(throwables), k=n))
        return str(eqo)

    def stratagems(self, by_type: StratagemType | None = None, by_subtype: StratagemSubtype | None = None, n: int = 1):
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

    def booster(self, n: int = 1):
        eqo = EquipmentOrder(random.sample(list(self.catalog.boosters['all']), k=n))
        return eqo

    def armor(self, by_weight: ArmorWeight | None = None, n: int = 1):
        if by_weight is None:
            armors = self.catalog.armor['all']
        else:
            armors = self.catalog.armor['weights'][by_weight.name]
        eqo = EquipmentOrder(random.sample(list(armors), k=n))
        return str(eqo)

    @staticmethod
    def faction_order(*args, **kwargs):
        return str(FactionOrder(*args, **kwargs))

    @staticmethod
    def difficulty_order(*args, **kwargs):
        return str(DifficultyOrder(*args, **kwargs))

    @staticmethod
    def planet_order(*args, **kwargs):
        return str(PlanetOrder(*args, **kwargs))

