import random
from enum import IntEnum, StrEnum
from collections import defaultdict
from registration import PlayerRegistry, EquipmentCatalog


class Randomizer:
    Factions = {
        'Terminids': ['Rupture Strain', 'Spore Burst', 'Predator Strain'],
        'Automatons': ['Jet Brigade', 'Incineration Corps', 'Cyborg Legion'],
        'Illuminate': ['Mindless Masses', 'Appropriators'],
    }
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
        'Tundra': [],
        'Basic Swamp': ['Rainstorms'],
        'Haunted Swamp': ['Thick Fog'],
        'Autumn Forest': [],
        'Deciduous Forest': [],
    }

    OperationalModifiers = ['Complex Stratagem Plotting', 'Orbital Fluctuations',
                            'Poor Intel', 'Civilians in SEAF Areas']

    BiomesByCondition = defaultdict(list)
    for biome, conditions in ConditionsByBiome.items():
        for condition in conditions:
            BiomesByCondition[condition].append(biome)


    def __init__(self, registry: PlayerRegistry, catalog: EquipmentCatalog):
        self.registry = registry
        self.catalog = catalog

    def order(self):
        pass
