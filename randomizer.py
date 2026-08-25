import random
from registration import PlayerRegistry, EquipmentCatalog

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

    def __new__(cls):
        level = random.choice(cls.Distribution)
        return cls.Levels[level]



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

    def __init__(self):
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

    def __init__(self):
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

