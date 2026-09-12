from enum import StrEnum, nonmember, IntEnum, IntFlag, auto
from exceptions import UnknownRegistrationPreset, UnknownSlot, StratagemSubtypeMismatch, UnknownEquipmentSource, \
    UnknownStratagemSubtype, UnknownArmorWeight

from utils import prefix_match


class EnumEvalRepr:
    name: str
    def __repr__(self):
        return f'{self.__class__.__name__}.{self.name}'


class Passive(StrEnum, EnumEvalRepr):
    Acclimated = "Acclimated"
    AdrenoDefibrillator = "Adreno-Defibrillator"
    AdvancedFiltration = "Advanced Filtration"
    BallisticPadding = "Ballistic Padding"
    ConcussivePaddingGrenadier = "Concussive Padding, Grenadier"
    ConcussivePaddingHazmat = "Concussive Padding, Hazmat"
    ConcussivePaddingReinforced = "Concussive Padding, Reinforced"
    DemocracyProtects = "Democracy Protects"
    DesertStormer = "Desert Stormer"
    ElectricalConduit = "Electrical Conduit"
    EngineeringKit = "Engineering Kit"
    ExtraPadding = "Extra Padding"
    FeetFirst = "Feet First"
    Fortified = "Fortified"
    Gunslinger = "Gunslinger"
    Inflammable = "Inflammable"
    IntegratedExplosives = "Integrated Explosives"
    KineticDisplacementMitigation = "Kinetic Displacement Mitigation"
    MedKit = "Med-Kit"
    Oxygenator = "Oxygenator"
    PeakPhysique = "Peak Physique"
    ReducedSignature = "Reduced Signature"
    ReinforcedEpaulettes = "Reinforced Epaulettes"
    RockSolid = "Rock Solid"
    Scout = "Scout"
    ServoAssisted = "Servo-Assisted"
    SiegeReady = "Siege-Ready"
    SupplementaryAdrenaline = "Supplementary Adrenaline"
    TrueGrit = "True Grit"
    Unflinching = "Unflinching"

    def styles(self) -> set[Style]:
        s = []
        match self:
            case self.Acclimated: s.extend([Style.Pyrotechnician, Style.Electrician, Style.Fumigator])
            case self.AdrenoDefibrillator: s.extend([Style.Survivalist, Style.Medic])
            case self.AdvancedFiltration: s.extend([Style.Fumigator, Style.Trapper])
            case self.BallisticPadding: s.extend(Style)
            case self.ConcussivePaddingGrenadier: s.extend([Style.Demolitionist, Style.Grenadier])
            case self.ConcussivePaddingHazmat: s.extend([Style.Demolitionist, Style.Fumigator, Style.Trapper])
            case self.ConcussivePaddingReinforced: s.extend([Style.Demolitionist, Style.Survivalist])
            case self.DemocracyProtects: s.extend(Style)
            case self.DesertStormer: s.extend([Style.Pyrotechnician, Style.Electrician, Style.Fumigator, Style.Grenadier, Style.Spotter])
            case self.ElectricalConduit: s.extend([Style.Electrician])
            case self.EngineeringKit: s.extend([Style.Sniper, Style.Juggernaut, Style.Grenadier])
            case self.ExtraPadding: s.extend(Style)
            case self.FeetFirst: s.extend([Style.Infiltrator, Style.Scout])
            case self.Fortified: s.extend([Style.Sniper, Style.Juggernaut, Style.Demolitionist, Style.Cleanser])
            case self.Gunslinger: s.extend([Style.Lawnmower, Style.Brawler, Style.Sheriff])
            case self.Inflammable: s.append(Style.Pyrotechnician)
            case self.IntegratedExplosives: s.extend([Style.Demolitionist, Style.Grenadier])
            case self.KineticDisplacementMitigation: s.extend([Style.Pyrotechnician, Style.Survivalist])
            case self.MedKit: s.extend([Style.Medic, Style.Survivalist, Style.Soloist])
            case self.Oxygenator: s.extend([Style.Scout, Style.Infiltrator, Style.Soloist, Style.Sheriff])
            case self.PeakPhysique: s.extend([Style.Brawler, Style.Sniper, Style.Infiltrator, Style.Juggernaut, Style.Bouncer, Style.Pilot, Style.Driver])
            case self.ReducedSignature: s.extend([Style.Scout, Style.Infiltrator])
            case self.ReinforcedEpaulettes: s.extend([Style.Survivalist, Style.Brawler, Style.Infiltrator])
            case self.RockSolid: s.extend([Style.Brawler, Style.Infiltrator, Style.Bouncer])
            case self.Scout: s.extend([Style.Scout, Style.Infiltrator, Style.Spotter])
            case self.ServoAssisted: s.extend([Style.Grenadier, Style.Spotter])
            case self.SiegeReady: s.extend([Style.Juggernaut, Style.Lawnmower, Style.Bouncer, Style.Sheriff, Style.Cleanser, Style.Brawler, Style.Sniper])
            case self.SupplementaryAdrenaline: s.extend([Style.Survivalist, Style.Medic])
            case self.TrueGrit: s.extend([Style.Juggernaut, Style.Sniper, Style.Logistician])
            case self.Unflinching: s.extend(Style)
        return set(s)

class PrimaryType(StrEnum, EnumEvalRepr):
    AR = "Assault Rifle"
    MR = "Marksman Rifle"
    SMG = "Submachine Gun"
    SG = "Shotgun"
    EXPL = "Explosive"
    EB = "Energy-Based"
    SP = "Special"

    @classmethod
    def from_string(cls, primary_type: str):
        s = primary_type.casefold()
        for pt in cls:
            if pt.name.casefold().startswith(s) or pt.value.casefold().startswith(s):
                return pt
        return cls.AR


class SecondaryType(IntEnum, EnumEvalRepr):
    Pistol = 1
    Melee = 2
    Special = 3

    @classmethod
    def from_string(cls, secondary_type: str):
        s = secondary_type.casefold()
        for st in cls:
            if st.name.casefold().startswith(s):
                return s
        return cls.Pistol


class ThrowableType(StrEnum, EnumEvalRepr):
    STD = 'Standard'
    SL = 'Special'

    @classmethod
    def from_string(cls, throwable_type: str):
        s = throwable_type.casefold()
        for tt in cls:
            if tt.name.casefold().startswith(s) or tt.value.casefold().startswith(s):
                return tt
        return cls.STD


def _initialize_presets(cls):
    cls._make_preset_sources()
    return cls


@_initialize_presets
class RegPreset(StrEnum, EnumEvalRepr):
    Classic = "OG"  # Stock equipment, event items, and Helldivers Mobilize! only
    Enthusiast = "ET"  # Classic + all non-legendary warbonds
    Collector = "CL"  # Enthusiast + all legendary warbonds
    Armorer = "AM"  # Collector + all superstore items
    Quartermaster = "QM"  # Armorer + Super Citizen edition
    Veteran = "VT"  # Quartermaster + preorder bonuses

    def description(self):
        d = "Default equipment, event rewards, super destroyer equipment, and Helldivers Mobilize"
        match self:
            case self.Enthusiast:
                d = "All items from **Classic** + all non-legendary warbonds"
            case self.Collector:
                d = "All items from **Enthusiast** + all legendary warbonds"
            case self.Armorer:
                d = "All items from **Collector** + all Super Store items"
            case self.Quartermaster:
                d = "All items from **Armorer** + Super Citizen Edition"
            case self.Veteran:
                d = "All items from **Quartermaster** + Preorder bonuses"
        return d

    PresetSources = nonmember(None)

    @classmethod
    def from_string(cls, preset_name: str):
        s = preset_name.casefold()
        for rp in cls:
            if rp.name.casefold().startswith(s) or rp.value.casefold().startswith(s):
                return rp
        return cls.Classic

    def sources(self):
        return self.PresetSources[self]

    @classmethod
    def _make_preset_sources(cls):
        mapping = {cls.Classic: [Source.Stock, Source.EV, Source.HM, Source.SDD]}

        mapping[cls.Enthusiast] = mapping[cls.Classic] + [
            Source.BJ, Source.CA, Source.CE, Source.CE, Source.CG,
            Source.DD, Source.DUDE, Source.ED, Source.EE, Source.FF,
            Source.FL, Source.MC, Source.MC, Source.PC, Source.PP,
            Source.RR, Source.SB, Source.SF, Source.SV, Source.TE,
            Source.UL, Source.VC
        ]

        mapping[cls.Collector] = mapping[cls.Enthusiast] + [
            Source.KZ, Source.WH, Source.ODST,
        ]

        mapping[cls.Armorer] = mapping[cls.Collector] + [Source.SS]
        mapping[cls.Quartermaster] = mapping[cls.Armorer] + [Source.SCE]
        mapping[cls.Veteran] = mapping[cls.Quartermaster] + [Source.PB]
        cls.PresetSources = mapping


class Slot(StrEnum, EnumEvalRepr):
    Primary = "primary"
    Secondary = "secondary"
    Throwable = "throwable"
    Booster = "booster"
    Armor = "armor"
    Stratagem = "stratagem"


class StratagemType(IntEnum, EnumEvalRepr):
    Supply = 1
    Vehicle = 2
    Defensive = 3
    Offensive = 4

    @classmethod
    def from_string(cls, stratagem_type: str):
        s = stratagem_type.casefold()
        for st in cls:
            if st.name.casefold().startswith(s):
                return st
        return cls.Offensive


class Source(StrEnum, EnumEvalRepr):
    # Included with the game
    Stock = 'Default Equipment'
    HM = 'Helldivers Mobilize'
    EV = 'Event Rewards'

    # Standard warbonds
    SV = 'Steeled Veterans'
    CE = 'Cutting Edge'
    DD = 'Democratic Detonation'
    PP = 'Polar Patriots'
    VC = 'Viper Commandos'
    FF = "Freedom's Flame"
    CA = 'Chemical Agents'
    TE = 'Truth Enforcers'
    UL = 'Urban Legends'
    SF = 'Servants of Freedom'
    BJ = 'Borderline Justice'
    MC = 'Masters of Ceremony'
    FL = 'Force of Law'
    CG = 'Control Group'
    DUDE = 'Dust Devils'
    PC = 'Python Commandos'
    RR = 'Redacted Regiment'
    SB = 'Siege Breakers'
    ED = 'Entrenched Division'
    EE = 'Exo Experts'

    # Legendary warbonds
    ODST = 'Obedient Democracy Support Troopers'
    KZ = 'Righteous Revenants'
    WH = "Castellan's Creed"

    # Premium content
    SCE = 'Super Citizen Edition'
    PB = 'Preorder Bonus'
    SS_HM = 'Super Store [Helldivers Mobilize]'
    SS_SV = 'Super Store [Steeled Veterans]'
    SS_CE = 'Super Store [Cutting Edge]'
    SS_DD = 'Super Store [Democratic Detonation]'
    SS_PP = 'Super Store [Polar Patriots]'
    SS_VC = 'Super Store [Viper Commandos]'
    SS_FF = "Super Store [Freedom's Flame]"
    SS_CA = "Super Store [Chemical Agents]"
    SS_TE = 'Super Store [Truth Enforcers]'
    SS_UL = 'Super Store [Urban Legends]'
    SS_SF = 'Super Store [Servants of Freedom]'
    SS_BJ = 'Super Store [Borderline Justice]'
    SS_MC = 'Super Store [Masters of Ceremony]'
    SS_FL = 'Super Store [Force of Law]'
    SS_CG = 'Super Store [Control Group]'
    SS_DUDE = 'Super Store [Dust Devils]'
    SS_PC = 'Super Store [Python Commandos]'
    SS_RR = 'Super Store [Redacted Regiment]'
    SS_SB = 'Super Store [Siege Breakers]'
    SS_ED = 'Super Store [Entrenched Division]'
    SS_EE = 'Super Store [Exo Experts]'
    SS_NW = 'Super Store [Non-Warbond Page]'
    SS = 'Comines All Super Store Pages'

    # Super destroyer
    PAC = 'Patriotic Administration Center'
    EB = 'Engineering Bay'
    HG = 'Hangar'
    BR = 'Bridge'
    RW = 'Robotics Workshop'
    OC = 'Orbital Cannons'
    SDD = 'Combines `PAC`, `EB`, `HG`, `BR`, `RW`, and `OC`'

    @classmethod
    def from_string(cls, src: str):
        cf = src.casefold()
        for eq_src in cls:
            if eq_src.name.casefold().startswith(cf) or eq_src.value.casefold().startswith(cf):
                return eq_src
        raise UnknownEquipmentSource(f'No matching equipment source for `{src}`. Use'
                                     f' the command `viewsources` for information on equipment availability.')

    @classmethod
    def replace_shorthand(cls, eq_sources: list[Source]):
        if cls.SDD in eq_sources:
            eq_sources.remove(cls.SDD)
            eq_sources.extend([cls.PAC, cls.EB, cls.HG, cls.BR, cls.RW, cls.OC])
        if cls.SS in eq_sources:
            eq_sources.remove(cls.SS)
            for ev in cls:
                if ev.name.startswith('SS_'):
                    eq_sources.append(ev)


class StratagemSubtype(IntFlag, EnumEvalRepr):
    Weapon = auto()
    Backpack = auto()
    Exosuit = auto()
    FRV = auto()
    Tank = auto()
    Sentry = auto()
    Emplacement = auto()
    Minefield = auto()
    Eagle = auto()
    Orbital = auto()

    BackpackWeapon = Weapon | Backpack

    def type(self) -> StratagemType:
        st = StratagemType.Offensive
        match self:
            case self.Weapon | self.Backpack | self.BackpackWeapon:
                st = StratagemType.Supply
            case self.Exosuit | self.FRV | self.Tank:
                st = StratagemType.Vehicle
            case self.Sentry | self.Emplacement | self.Minefield:
                st = StratagemType.Defensive
        return st

    @classmethod
    def from_string(cls, subtype: str):
        cf = subtype.casefold()
        for sst in cls:
            if sst.name.casefold().startswith(cf):
                return sst
        raise UnknownStratagemSubtype(subtype)


class Weight(IntEnum, EnumEvalRepr):
    Light = 1
    Medium = 2
    Heavy = 3

    @classmethod
    def from_string(cls, weight: str):
        cf = weight.casefold()
        for wt in cls:
            if wt.name.casefold().startswith(cf):
                return wt
        return UnknownArmorWeight(weight)


class Style(StrEnum, EnumEvalRepr):
    Pilot = 'extraction, exosuits, and critical mission cargo'
    Driver = 'leadership, navigation, and wheeled vehicles'
    Cleanser = 'plasma weapons'
    Pyrotechnician = 'flame weapons'
    Demolitionist = 'explosives and destroying enemy structures'
    Electrician = 'arc and EMP weapons'
    Optician = 'lasers and heat-limited weapons'
    Fumigator = 'gas weapons'
    Sniper = 'long-range and scoped weapons'
    Infiltrator = 'smoke, melee weapons, and quiet firearms'
    Spotter = 'eagle and orbital stratagems'
    Scout = 'fast intelligence gathering'
    Engineer = 'drones, sentries, shields, and operating terminals'
    Medic = 'stims, support, and non-weapon backpacks'
    Grenadier = 'throwables and firearm-launched explosives'
    Trapper = 'mines and weapons with gas, stun, or EMP effects'
    Logistician = 'supplies, large magazines, and team reloads'
    Soloist = 'heat sink and ammoless weapons, drones, non-weapon backpacks, and large magazines'
    Brawler = 'short-range firearms and melee weapons'
    Juggernaut = 'heavy armor penetration and clearing armored cavalry'
    Lawnmower = 'light armor penetration and clearing light infantry'
    Bouncer = 'medium armor penetration and clearing heavy infantry'
    Sheriff = 'marksman rifles, sidearms, and urban combat'
    Survivalist = 'shrugging off damage'
    Artillerist = 'indirect fire and target suppression'
    Tracker = 'laser-guided or homing munitions'
    Helldiver = 'bringing our foes to justice'

    Elemental = nonmember({Pyrotechnician, Fumigator, Electrician})

class Odds(IntEnum, EnumEvalRepr):
    Common = 9
    Special = 3
    Rare = 1


class EquipmentItem:
    def __init__(self, name: str, source: Source, styles: set[Style], slot: Slot):
        self.name = name
        self.styles = styles
        self.styles.add(Style.Helldiver)
        self.source = source
        self.slot = slot
        self.designation = self.name.split(' ', 1)[0]

    def __hash__(self):
        return hash((self.__class__.__name__, self.slot, self.name))

    def __str__(self):
        return self.name

    def _args(self):
        return self.name, self.source, self.styles, self.slot

    def __repr__(self):
        clsname = self.__class__.__name__
        repr_args = [repr(a) for a in self._args()]
        return f'{clsname}({", ".join(repr_args)})'


class Armor(EquipmentItem):
    def __init__(self, name: str, source: Source, passive: Passive, weight: Weight):
        super().__init__(name, source, passive.styles(), Slot.Armor)
        self.slot_type = Slot.Armor
        self.passive = passive
        self.weight = weight

    def _repr_args(self):
        return self.name, self.source, self.passive, self.weight


class Booster(EquipmentItem):
    def __init__(self, name: str, source: Source, styles: set[Style]):
        super().__init__(name, source, styles, Slot.Booster)

    def _repr_args(self):
        return self.name, self.source, self.styles


class Primary(EquipmentItem):
    def __init__(self, name: str, source: Source, ptype: PrimaryType, styles: set[Style]):
        super().__init__(name, source, styles, Slot.Primary)
        self.type = ptype

    def _repr_args(self):
        return self.name, self.source, self.type, self.styles


class Secondary(EquipmentItem):
    def __init__(self, name: str, source: Source, stype: SecondaryType, styles: set[Style]):
        super().__init__(name, source, styles, Slot.Secondary)
        self.type = stype

    def _repr_args(self):
        return self.name, self.source, self.type, self.styles


class Throwable(EquipmentItem):
    def __init__(self, name: str, source: Source, ttype: ThrowableType, styles: set[Style]):
        super().__init__(name, source, styles, Slot.Throwable)
        self.type = ttype

    def _repr_args(self):
        return self.name, self.source, self.type, self.styles


class Stratagem(EquipmentItem):
    def __init__(self, name: str, source: Source, sst: StratagemSubtype, styles: set[Style]):
        super().__init__(name, source, styles, Slot.Stratagem)
        self.type = sst.type()
        self.subtype = sst

    def _repr_args(self):
        return self.name, self.source, self.subtype, self.styles


