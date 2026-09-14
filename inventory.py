import utils
from enum import StrEnum, nonmember, IntEnum, auto, IntFlag
from typing import Iterable, Self
from exceptions import UnknownEquipmentSource, UnknownStratagemSubtype, UnknownArmorWeight


class EnumEvalRepr:
    name: str
    def __repr__(self):
        return f'{self.__class__.__name__}.{self.name}'


class PrimaryType(EnumEvalRepr, StrEnum):
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


class SecondaryType(EnumEvalRepr, IntEnum):
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


class ThrowableType(EnumEvalRepr, StrEnum):
    STD = 'Standard'
    SL = 'Special'

    @classmethod
    def from_string(cls, throwable_type: str):
        s = throwable_type.casefold()
        for tt in cls:
            if tt.name.casefold().startswith(s) or tt.value.casefold().startswith(s):
                return tt
        return cls.STD


class Slot(EnumEvalRepr, StrEnum):
    Primary = "primary"
    Secondary = "secondary"
    Throwable = "throwable"
    Booster = "booster"
    Armor = "armor"
    Stratagem = "stratagem"

    @classmethod
    def from_string(cls, s: str) -> Slot:
        cf = s.casefold()
        for ev in cls:
            if utils.prefix_match(ev, cf):
                return ev
        return cls.Stratagem

    def required(self):
        """Return the number of items required to fill this loadout slot."""
        if self is self.Stratagem:
            return 4
        return 1

    def sort_key(self):
        """Return a number used for ordering slots consistently."""
        match self:
            case self.Primary:
                return 1
            case self.Secondary:
                return 2
            case self.Throwable:
                return 3
            case self.Stratagem:
                return 4
            case self.Booster:
                return 5
            case self.Armor:
                return 6


class StratagemType(EnumEvalRepr, IntEnum):
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


class StratagemSubtype(EnumEvalRepr, IntFlag):
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
        """Return the parent StratagemType."""
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


class Weight(EnumEvalRepr, IntEnum):
    Light = 1
    Medium = 2
    Heavy = 3

    def __str__(self) -> str:
        return self.name

    @classmethod
    def from_string(cls, weight: str):
        cf = weight.casefold()
        for wt in cls:
            if wt.name.casefold().startswith(cf):
                return wt
        return UnknownArmorWeight(weight)


class Style(EnumEvalRepr, StrEnum):
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

    @classmethod
    def elemental(cls):
        return {cls.Pyrotechnician, cls.Fumigator, cls.Electrician}

class Odds(EnumEvalRepr, IntEnum):
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
        parts = self.name.split(' ')
        self.designation = parts[0]
        self.shortname = ''.join(p.capitalize() for p in parts[1:])

    def __hash__(self):
        return hash((self.__class__.__name__, self.slot, self.name))

    def __str__(self):
        return self.name

    def _repr_args(self):
        return self.name, self.source, self.styles, self.slot

    def __repr__(self):
        clsname = self.__class__.__name__
        repr_args = [repr(a) for a in self._repr_args()]
        return f'{clsname}({", ".join(repr_args)})'


class Armor(EquipmentItem):
    def __init__(self, name: str, source: Source, passive: Passive, weight: Weight):
        super().__init__(name, source, passive.styles(), Slot.Armor)
        self.slot_type = Slot.Armor
        self.passive = passive
        self.weight = weight

    def __str__(self):
        return f'{self.name} [{self.weight}/{self.passive}]'

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
        if self.subtype in {StratagemSubtype.Eagle, StratagemSubtype.Orbital}:
            parts = name.split(' ')
            self.shortname = ''.join(p.capitalize() for p in parts[1:])
            self.designation = ''.join(p.capitalize() for p in parts[:2])

    def _repr_args(self):
        return self.name, self.source, self.subtype, self.styles


AnyEquipment = Primary | Secondary | Throwable | Stratagem | Armor | Booster | EquipmentItem


class Source(EnumEvalRepr, StrEnum):
    BASE = '[Unlocked]'
    STOCK = 'Default Equipment'
    HM = 'Helldivers Mobilize'

    SDD = '[Unlockable]'
    PAC = 'Patriotic Administration Center'
    EB = 'Engineering Bay'
    HG = 'Hangar'
    BR = 'Bridge'
    RW = 'Robotics Workshop'
    OC = 'Orbital Cannons'

    EVENT = '[Event Items]'
    EV_CT = 'Census Thunder'
    EV_CF = 'Celestial Fence'
    EV_LI = 'Lightning Intercept'
    EV_PE = 'Permanent Enclosure'
    EV_VP = 'Void Piercer'
    EV_CH = 'Counterdissident Hammer'
    EV_BE = 'Blazing Electorate'

    WAR = '[Standard Warbonds]'
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
    LEG = '[Legendary Warbonds]'
    ODST = 'Obedient Democracy Support Troopers'
    KZ = 'Righteous Revenants'
    WH = "Castellan's Creed"

    # Premium content
    PAID = '[Paid Content]'
    SCE = 'Super Citizen Edition'
    PB = 'Preorder Bonus'

    SS = '[Super Store]'
    SS_HM = '[$] Helldivers Mobilize'
    SS_SV = '[$] Steeled Veterans'
    SS_CE = '[$] Cutting Edge'
    SS_DD = '[$] Democratic Detonation'
    SS_PP = '[$] Polar Patriots'
    SS_VC = '[$] Viper Commandos'
    SS_FF = "[$] Freedom's Flame"
    SS_CA = "[$] Chemical Agents"
    SS_TE = '[$] Truth Enforcers'
    SS_UL = '[$] Urban Legends'
    SS_SF = '[$] Servants of Freedom'
    SS_BJ = '[$] Borderline Justice'
    SS_MC = '[$] Masters of Ceremony'
    SS_FL = '[$] Force of Law'
    SS_CG = '[$] Control Group'
    SS_DUDE = '[$] Dust Devils'
    SS_PC = '[$] Python Commandos'
    SS_RR = '[$] Redacted Regiment'
    SS_SB = '[$] Siege Breakers'
    SS_ED = '[$] Entrenched Division'
    SS_EE = '[$] Exo Experts'
    SS_NW = '[$] Non-Warbond Pages'

    OTHER = '[Other]'
    GIFT = 'Granted by Arrowhead'

    ALL = '[[Everything]]'

    @classmethod
    def from_string(cls, src: str) -> Source:
        cf = src.casefold()
        for eq_src in cls:
            if eq_src.name.casefold().startswith(cf) or eq_src.value.casefold().startswith(cf):
                return eq_src
        raise UnknownEquipmentSource(f'No matching equipment source for `{src}`. Use'
                                     f' the command `viewsources` for information on equipment availability.')

    def replacements(self) -> list[Source]:
        replacements = []
        if self is self.ALL or self is self.BASE:
            replacements.extend([self.STOCK, self.HM])
        if self is self.ALL or self is self.SDD:
            replacements.extend([self.PAC, self.HG, self.RW, self.EB, self.BR, self.OC])
        if self is self.ALL or self is self.EVENT:
            replacements.extend([self.EV_CT, self.EV_CF, self.EV_LI, self.EV_PE, self.EV_VP, self.EV_CH, self.EV_BE])
        if self is self.ALL or self is self.WAR:
            replacements.extend([self.SV, self.CE, self.DD, self.PP, self.VC, self.FF,
                                 self.CA, self.TE, self.UL, self.SF, self.BJ, self.MC, self.FL,
                                 self.CG, self.DUDE, self.PC, self.RR, self.SB, self.ED, self.EE])
        if self is self.ALL or self is self.LEG:
            replacements.extend([self.ODST, self.KZ, self.WH])
        if self is self.ALL or self is self.PAID:
            replacements.extend([self.SCE, self.PB])
        if self is self.ALL or self is self.SS:
            replacements.extend([self.SS_HM, self.SS_SV, self.SS_CE, self.SS_DD, self.SS_PP,
                                 self.SS_VC, self.SS_FF, self.SS_CA, self.SS_TE, self.SS_UL,
                                 self.SS_SF, self.SS_BJ, self.SS_MC, self.SS_FL, self.SS_CG,
                                 self.SS_DUDE, self.SS_PC, self.SS_RR, self.SS_SB, self.SS_ED,
                                 self.SS_EE, self.SS_NW])
        if self is self.ALL or self is self.OTHER:
            replacements.extend([self.GIFT])
        return replacements


    @classmethod
    def replace_shorthand(cls, eq_sources: list[Source]):
        print('eq_sources:', eq_sources)
        replacement_mapping = {}
        for eq_source in eq_sources:
            if repl := eq_source.replacements():
                replacement_mapping[eq_source] = repl

        for shorthand, replacements in replacement_mapping.items():
            if shorthand in eq_sources:
                eq_sources.remove(shorthand)
                eq_sources.extend(replacements)



class SourceGroup(StrEnum):
    All = 'All equipment sources'
    Basic = 'Stock equipment sources + Helldivers Mobilize'
    SuperDestroyer = 'Super destroyer stratagems'
    Campaign = 'Campaign rewards'
    Warbonds = 'Regular warbonds'
    Legendary = 'Legendary warbonds'
    SuperStore = 'Super store pages'
    Premium = 'Preorder bonuses + Super Citizen Edition'
    Etc = 'Anniversary gifts and miscellanea'

    def sources(self) -> list[Source]:
        mapping = {
            self.Basic: Source.BASE,
            self.SuperDestroyer: Source.SDD,
            self.Campaign: Source.EVENT,
            self.Warbonds: Source.WAR,
            self.Legendary: Source.LEG,
            self.SuperStore: Source.SS,
            self.Premium: Source.PAID,
            self.Etc: Source.OTHER,
        }
        if self is self.All:
            sources = [Source.ALL]
            for sg, src in mapping.items():
                sources.append(src)
                sources.extend(src.replacements())
            return sources
        return [x := mapping[self]] + x.replacements()


    @classmethod
    def from_string(cls, sg: str) -> SourceGroup:
        cf = sg.casefold()
        for ev in cls:
            if utils.prefix_match(ev, cf):
                return ev
        return cls.All


class Passive(EnumEvalRepr, StrEnum):
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

    @classmethod
    def elemental(cls):
        return {cls.Inflammable, cls.Acclimated, cls.ElectricalConduit, cls.DesertStormer, cls.AdvancedFiltration}

    def __str__(self):
        return self.value

    def styles(self) -> set[Style]:
        s = []
        match self:
            case self.Acclimated: s.extend([Style.Pyrotechnician, Style.Electrician, Style.Fumigator])
            case self.AdrenoDefibrillator: s.extend([Style.Survivalist, Style.Medic])
            case self.AdvancedFiltration: s.extend([Style.Fumigator])
            case self.BallisticPadding: s.extend(set(Style) - Style.elemental())
            case self.ConcussivePaddingGrenadier: s.extend([Style.Demolitionist, Style.Grenadier])
            case self.ConcussivePaddingHazmat: s.extend([Style.Demolitionist, Style.Fumigator, Style.Trapper])
            case self.ConcussivePaddingReinforced: s.extend([Style.Demolitionist, Style.Survivalist])
            case self.DemocracyProtects: s.extend(set(Style) - Style.elemental())
            case self.DesertStormer: s.extend([Style.Pyrotechnician, Style.Electrician, Style.Fumigator])
            case self.ElectricalConduit: s.extend([Style.Electrician])
            case self.EngineeringKit: s.extend([Style.Sniper, Style.Juggernaut, Style.Grenadier, Style.Engineer])
            case self.ExtraPadding: s.extend(set(Style) - Style.elemental())
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
            case self.Unflinching: s.extend([Style.Juggernaut, Style.Sheriff])
        return set(s)


_Equipment = [
    Armor('B-01 Tactical', Source.STOCK, Passive.ExtraPadding, Weight.Medium),
    Armor('AC-2 Obedient', Source.KZ, Passive.Acclimated, Weight.Light),
    Armor('AC-1 Dutiful', Source.KZ, Passive.Acclimated, Weight.Medium),
    Armor('AD-26 Bleeding Edge', Source.CG, Passive.AdrenoDefibrillator, Weight.Medium),
    Armor('AD-11 Livewire', Source.CG, Passive.AdrenoDefibrillator, Weight.Light),
    Armor('AD-49 Apollonian', Source.CG, Passive.AdrenoDefibrillator, Weight.Heavy),
    Armor('AF-50 Noxious Ranger', Source.CA, Passive.AdvancedFiltration, Weight.Light),
    Armor('AF-91 Field Chemist', Source.SS_CA, Passive.AdvancedFiltration, Weight.Medium),
    Armor('AF-02 Haz-Master', Source.CA, Passive.AdvancedFiltration, Weight.Medium),
    Armor('AF-Lockdown', Source.SS_CA, Passive.AdvancedFiltration, Weight.Heavy),
    Armor('BP-32 Jackboot', Source.FL, Passive.BallisticPadding, Weight.Light),
    Armor('BP-20 Correct Officer', Source.FL, Passive.BallisticPadding, Weight.Medium),
    Armor('BP-77 Grand Juror', Source.SS_FL, Passive.BallisticPadding, Weight.Heavy),
    Armor('CPG-48 Sapper', Source.ED, Passive.ConcussivePaddingGrenadier, Weight.Medium),
    Armor('CPH-26 Commandant', Source.ED, Passive.ConcussivePaddingHazmat, Weight.Light),
    Armor('CPR-80 Bulwark', Source.SS, Passive.ConcussivePaddingReinforced, Weight.Heavy),
    Armor('DP-53 Savior of the Free', Source.SCE, Passive.DemocracyProtects, Weight.Medium),
    Armor('DP-40 Hero of the Federation', Source.HM, Passive.DemocracyProtects, Weight.Medium),
    Armor('DP-11 Champion of the People', Source.HM, Passive.DemocracyProtects, Weight.Medium),
    Armor('DP-00 Tactical', Source.STOCK, Passive.DemocracyProtects, Weight.Medium),
    Armor('B-22 Model Citizen', Source.GIFT, Passive.DemocracyProtects, Weight.Medium),
    Armor('DS-10 Big Game Hunter', Source.SS_DUDE, Passive.DesertStormer, Weight.Light),
    Armor('DS-191 Scorpion', Source.DUDE, Passive.DesertStormer, Weight.Medium),
    Armor("DS-42 Federation's Blade", Source.DUDE, Passive.DesertStormer, Weight.Heavy),
    Armor('EX-00 Prototype X', Source.CE, Passive.ElectricalConduit, Weight.Light),
    Armor('EX-03 Prototype 3', Source.CE, Passive.ElectricalConduit, Weight.Medium),
    Armor('EX-16 Prototype 16', Source.CE, Passive.ElectricalConduit, Weight.Medium),
    Armor('CE-74 Breaker', Source.SS_SV, Passive.EngineeringKit, Weight.Light),
    Armor('CE-67 Titan', Source.SS_CE, Passive.EngineeringKit, Weight.Light),
    Armor('CE-07 Demolition Specialist', Source.DD, Passive.EngineeringKit, Weight.Light),
    Armor('FS-37 Ravager', Source.SS_DD, Passive.EngineeringKit, Weight.Light),
    Armor('SC-15 Drone Master', Source.SS_SV, Passive.EngineeringKit, Weight.Medium),
    Armor('CE-35 Trench Engineer', Source.HM, Passive.EngineeringKit, Weight.Medium),
    Armor('CE-81 Juggernaut', Source.SS_HM, Passive.EngineeringKit, Weight.Medium),
    Armor('CE-27 Ground Breaker', Source.DD, Passive.EngineeringKit, Weight.Medium),
    Armor('CE-101 Guerilla Gorilla', Source.SS_VC, Passive.EngineeringKit, Weight.Heavy),
    Armor('B-08 Light Gunner', Source.SS_HM, Passive.ExtraPadding, Weight.Light),
    Armor('TR-7 Ambassador of the Brand', Source.PB, Passive.ExtraPadding, Weight.Medium),
    Armor('TR-9 Cavalry of Democracy', Source.PB, Passive.ExtraPadding, Weight.Medium),
    Armor('CW-9 White Wolf', Source.SS_PP, Passive.ExtraPadding, Weight.Medium),
    Armor('TR-40 Gold Eagle', Source.GIFT, Passive.ExtraPadding, Weight.Medium),
    Armor('B-27 Fortified Commando', Source.SS_SV, Passive.ExtraPadding, Weight.Heavy),
    Armor('A-9 Helljumper', Source.ODST, Passive.FeetFirst, Weight.Medium),
    Armor('A-35 Recon', Source.ODST, Passive.FeetFirst, Weight.Medium),
    Armor('FS-38 Eradicator', Source.SS_SV, Passive.Fortified, Weight.Light),
    Armor('B-24 Enforcer', Source.SS_SV, Passive.Fortified, Weight.Medium),
    Armor('FS-34 Exterminator', Source.SS_HM, Passive.Fortified, Weight.Medium),
    Armor('FS-05 Marksman', Source.HM, Passive.Fortified, Weight.Heavy),
    Armor('FS-23 Battle Master', Source.HM, Passive.Fortified, Weight.Heavy),
    Armor('FS-11 Executioner', Source.SS_HM, Passive.Fortified, Weight.Heavy),
    Armor('FS-55 Devastator', Source.DD, Passive.Fortified, Weight.Heavy),
    Armor('CW-22 Kodiak', Source.PP, Passive.Fortified, Weight.Heavy),
    Armor("GS-11 Democracy's Deputy", Source.SS_BJ, Passive.Gunslinger, Weight.Light),
    Armor('GS-17 Frontier Marshal', Source.BJ, Passive.Gunslinger, Weight.Medium),
    Armor('GS-66 Lawmaker', Source.BJ, Passive.Gunslinger, Weight.Heavy),
    Armor('I-09 Heatseeker', Source.FF, Passive.Inflammable, Weight.Light),
    Armor('I-92 Fire Fighter', Source.SS_FF, Passive.Inflammable, Weight.Medium),
    Armor('I-102 Draconaught', Source.FF, Passive.Inflammable, Weight.Medium),
    Armor('I-44 Salamander', Source.SS_FF, Passive.Inflammable, Weight.Heavy),
    Armor('IE-57 Hell Bent', Source.SS_SF, Passive.IntegratedExplosives, Weight.Light),
    Armor('IE-3 Martyr', Source.SF, Passive.IntegratedExplosives, Weight.Medium),
    Armor('IE-12 Righteous', Source.SF, Passive.IntegratedExplosives, Weight.Medium),
    Armor('KDM-500 Outrider', Source.EV_PE, Passive.KineticDisplacementMitigation, Weight.Heavy),
    Armor('CM-21 Trench Paramedic', Source.SS_HM, Passive.MedKit, Weight.Light),
    Armor('TR-117 Alpha Commander', Source.STOCK, Passive.MedKit, Weight.Medium),
    Armor('CM-09 Bonesnapper', Source.HM, Passive.MedKit, Weight.Medium),
    Armor('CM-14 Physician', Source.HM, Passive.MedKit, Weight.Medium),
    Armor('CM-10 Clinician', Source.SS_DD, Passive.MedKit, Weight.Medium),
    Armor('CM-17 Butcher', Source.SS_CE, Passive.MedKit, Weight.Heavy),
    Armor('O-3 Free Spirit', Source.EE, Passive.Oxygenator, Weight.Light),
    Armor('O-44 Bonded Pilot', Source.SS_EE, Passive.Oxygenator, Weight.Medium),
    Armor('O-2 Heavy Operator', Source.EE, Passive.Oxygenator, Weight.Heavy),
    Armor('PH-9 Predator', Source.VC, Passive.PeakPhysique, Weight.Light),
    Armor('PH-56 Jaguar', Source.SS_VC, Passive.PeakPhysique, Weight.Medium),
    Armor('PH-202 Twigsnapper', Source.VC, Passive.PeakPhysique, Weight.Medium),
    Armor('RS-100 Sanctioner', Source.SS_RR, Passive.ReducedSignature, Weight.Light),
    Armor('RS-89 Shadow Paragon', Source.RR, Passive.ReducedSignature, Weight.Light),
    Armor('RS-67 Null Cipher', Source.RR, Passive.ReducedSignature, Weight.Medium),
    Armor('RE-1861 Parade Commander', Source.MC, Passive.ReinforcedEpaulettes, Weight.Light),
    Armor('RE-2310 Honrary Guard', Source.MC, Passive.ReinforcedEpaulettes, Weight.Medium),
    Armor('RE-824 Bearer of the Standard', Source.SS_MC, Passive.ReinforcedEpaulettes, Weight.Heavy),
    Armor('RS-20 Constrictor', Source.PC, Passive.RockSolid, Weight.Light),
    Armor('RS-6 Fiend Destroyer', Source.SS_PC, Passive.RockSolid, Weight.Medium),
    Armor('RS-40 Beast of Prey', Source.PC, Passive.RockSolid, Weight.Heavy),
    Armor('SC-34 Infiltrator', Source.HM, Passive.Scout, Weight.Light),
    Armor('SC-30 Trailblazer Scout', Source.HM, Passive.Scout, Weight.Light),
    Armor('CW-4 Arctic Ranger', Source.PP, Passive.Scout, Weight.Light),
    Armor('SA-04 Combat Technician', Source.HM, Passive.Scout, Weight.Medium),
    Armor('SC-37 Legionnaire', Source.SS_SV, Passive.ServoAssisted, Weight.Light),
    Armor('SA-25 Steel Trooper', Source.SV, Passive.ServoAssisted, Weight.Medium),
    Armor('SA-12 Servo-Assisted', Source.SV, Passive.ServoAssisted, Weight.Medium),
    Armor('TR-62 Knight', Source.PB, Passive.ServoAssisted, Weight.Heavy),
    Armor('SA-32 Dynamo', Source.SV, Passive.ServoAssisted, Weight.Heavy),
    Armor('FS-61 Dreadnought', Source.SS_HM, Passive.ServoAssisted, Weight.Heavy),
    Armor('CW-36 Winter Warrior', Source.PP, Passive.ServoAssisted, Weight.Heavy),
    Armor('SR-24 Street Scout', Source.UL, Passive.SiegeReady, Weight.Light),
    Armor('DP-8 Mountain Scaled', Source.SS_NW, Passive.SiegeReady, Weight.Medium),
    Armor('SR-62 Cinderblock', Source.SS_UL, Passive.SiegeReady, Weight.Heavy),
    Armor('SR-18 Roadblock', Source.UL, Passive.SiegeReady, Weight.Heavy),
    Armor('SA-7 Headfirst', Source.SB, Passive.SupplementaryAdrenaline, Weight.Medium),
    Armor('SA-8 Ram', Source.SB, Passive.SupplementaryAdrenaline, Weight.Heavy),
    Armor('TG-8 Sharpshooter', Source.WH, Passive.TrueGrit, Weight.Medium),
    Armor('TG-122 Demo-Trooper', Source.WH, Passive.TrueGrit, Weight.Medium),
    Armor('UF-16 Inspector', Source.TE, Passive.Unflinching, Weight.Light),
    Armor('UF-84 Doubt Killer', Source.SS_TE, Passive.Unflinching, Weight.Medium),
    Armor('UF-50 Bloodhound', Source.TE, Passive.Unflinching, Weight.Medium),
    Primary('AR-23 Liberator', Source.STOCK, PrimaryType.AR, {Style.Lawnmower, Style.Soloist}),
    Primary('AR-23P Liberator Penetrator', Source.HM, PrimaryType.AR, {Style.Bouncer}),
    Primary('AR-23C Liberator Concussive', Source.SV, PrimaryType.AR, {Style.Trapper}),
    Primary('StA-52 Assault Rifle', Source.KZ, PrimaryType.AR, {Style.Lawnmower}),
    Primary('AR-32 Pacifier', Source.FL, PrimaryType.AR, {Style.Bouncer, Style.Trapper}),
    Primary('AR-2 Coyote', Source.DUDE, PrimaryType.AR, {Style.Bouncer}),
    Primary('MA5C Assault Rifle', Source.ODST, PrimaryType.AR, {Style.Bouncer, Style.Brawler}),
    Primary('AR-23A Liberator Carbine', Source.VC, PrimaryType.AR, {Style.Lawnmower, Style.Brawler}),
    Primary('AR-59 Suppressor', Source.RR, PrimaryType.AR, {Style.Infiltrator, Style.Scout}),
    Primary('AR-61 Tenderizer', Source.PP, PrimaryType.AR, {Style.Bouncer, Style.Lawnmower, Style.Brawler}),
    Primary('AR/GL-21 One-Two', Source.PC, PrimaryType.AR, {Style.Demolitionist, Style.Bouncer, Style.Grenadier, Style.Lawnmower}),
    Primary('BR-14 Adjudicator', Source.DD, PrimaryType.AR, {Style.Bouncer}),
    Primary('R-2 Amendment', Source.MC, PrimaryType.MR, {Style.Sheriff, Style.Sniper, Style.Brawler, Style.Infiltrator}),
    Primary('R-2124 Constitution', Source.STOCK, PrimaryType.MR, {Style.Sheriff, Style.Sniper, Style.Brawler, Style.Infiltrator, Style.Bouncer}),
    Primary('R-4 Hyena', Source.EV_CF, PrimaryType.MR, {Style.Bouncer, Style.Sniper, Style.Sheriff}),
    Primary('R-6 Deadeye', Source.BJ, PrimaryType.MR, {Style.Sheriff, Style.Brawler, Style.Infiltrator}),
    Primary('R-63 Diligence', Source.HM, PrimaryType.MR, {Style.Sheriff, Style.Sniper}),
    Primary('R-63CS Diligence Counter Sniper', Source.HM, PrimaryType.MR, {Style.Sheriff, Style.Sniper, Style.Bouncer}),
    Primary('R-72 Censor', Source.RR, PrimaryType.MR, {Style.Infiltrator, Style.Sheriff, Style.Sniper}),
    Primary('M75 SMG', Source.ODST, PrimaryType.SMG, {Style.Sheriff, Style.Brawler, Style.Engineer, Style.Medic}),
    Primary('MP-98 Knight', Source.SCE, PrimaryType.SMG, {Style.Sheriff, Style.Brawler, Style.Engineer, Style.Medic}),
    Primary('SMG-203 Gallant', Source.EE, PrimaryType.SMG, {Style.Sheriff, Style.Bouncer, Style.Brawler, Style.Engineer, Style.Medic}),
    Primary('SMG-32 Reprimand', Source.TE, PrimaryType.SMG, {Style.Sheriff, Style.Bouncer, Style.Brawler}),
    Primary('SMG-37 Defender', Source.HM, PrimaryType.SMG, {Style.Lawnmower, Style.Medic, Style.Engineer}),
    Primary('SMG-72 Pummeler', Source.PP, PrimaryType.SMG, {Style.Trapper, Style.Lawnmower, Style.Medic, Style.Engineer}),
    Primary('SMG/FLAM-34 Stoker', Source.ED, PrimaryType.SMG, {Style.Pyrotechnician, Style.Medic, Style.Engineer}),
    Primary('StA-11 SMG', Source.KZ, PrimaryType.SMG, {Style.Lawnmower, Style.Brawler, Style.Medic, Style.Engineer}),
    Primary('DBS-2 Double Freedom', Source.SS_PC, PrimaryType.SG, {Style.Brawler, Style.Bouncer, Style.Demolitionist}),
    Primary('M90A Shotgun', Source.ODST, PrimaryType.SG, {Style.Brawler, Style.Bouncer}),
    Primary('SG-20 Halt', Source.TE, PrimaryType.SG, {Style.Brawler, Style.Trapper}),
    Primary('SG-225 Breaker', Source.HM, PrimaryType.SG, {Style.Lawnmower, Style.Brawler}),
    Primary('SG-225IE Breaker Incendiary', Source.SV, PrimaryType.SG, {Style.Lawnmower, Style.Brawler, Style.Soloist}),
    Primary('SG-225SP Breaker Spray&Pray', Source.HM, PrimaryType.SG, {Style.Lawnmower, Style.Brawler, Style.Soloist}),
    Primary('SG-451 Cookout', Source.FF, PrimaryType.SG, {Style.Brawler, Style.Trapper}),
    Primary('SG-8 Punisher', Source.HM, PrimaryType.SG, {Style.Brawler, Style.Trapper}),
    Primary('SG-8S Slugger', Source.HM, PrimaryType.SG, {Style.Brawler, Style.Bouncer, Style.Trapper}),
    Primary('SG-97 Sweeper', Source.ED, PrimaryType.SG, {Style.Brawler, Style.Bouncer, Style.Infiltrator}),
    Primary('CB-9 Exploding Crossbow', Source.DD, PrimaryType.EXPL, {Style.Sniper, Style.Demolitionist, Style.Bouncer}),
    Primary('R-36 Eruptor', Source.DD, PrimaryType.EXPL, {Style.Sniper, Style.Bouncer, Style.Juggernaut, Style.Demolitionist}),
    Primary('ARC-12 Blitzer', Source.CE, PrimaryType.EB, {Style.Electrician, Style.Bouncer, Style.Soloist}),
    Primary('LAS-13 Trident', Source.SB, PrimaryType.EB, {Style.Optician, Style.Soloist, Style.Brawler}),
    Primary('LAS-13 Sickle', Source.CE, PrimaryType.EB, {Style.Soloist, Style.Brawler, Style.Optician}),
    Primary('LAS-17 Double-Edge Sickle', Source.SF, PrimaryType.EB, {Style.Brawler, Style.Medic, Style.Optician}),
    Primary('LAS-5 Scythe', Source.HM, PrimaryType.EB, {Style.Sniper, Style.Optician, Style.Soloist}),
    Primary('PLAS-1 Scorcher', Source.HM, PrimaryType.EB, {Style.Bouncer, Style.Cleanser, Style.Demolitionist}),
    Primary('PLAS-101 Purifier', Source.PP, PrimaryType.EB, {Style.Bouncer, Style.Cleanser, Style.Demolitionist}),
    Primary('PLAS-39 Accelerator Rifle', Source.KZ, PrimaryType.EB, {Style.Sniper, Style.Cleanser, Style.Bouncer, Style.Demolitionist}),
    Primary('R/40-K Hot-Shot Marksman Rifle', Source.WH, PrimaryType.EB, {Style.Sniper, Style.Sheriff, Style.Bouncer, Style.Optician, Style.Cleanser}),
    Primary('SG-8P Punisher Plasma', Source.CE, PrimaryType.EB, {Style.Artillerist, Style.Bouncer, Style.Cleanser, Style.Demolitionist}),
    Primary('FLAM-66 Torcher', Source.FF, PrimaryType.SP, {Style.Brawler, Style.Pyrotechnician, Style.Bouncer, Style.Lawnmower}),
    Primary('JAR-5 Dominator', Source.SV, PrimaryType.SP, {Style.Sniper, Style.Bouncer, Style.Trapper}),
    Primary('VG-70 Variable', Source.CG, PrimaryType.SP, {Style.Juggernaut, Style.Brawler, Style.Medic, Style.Scout}),
    Secondary('M6C/SOCOM Pistol', Source.ODST, SecondaryType.Pistol, {Style.Infiltrator, Style.Scout}),
    Secondary('P-113 Verdict', Source.PP, SecondaryType.Pistol, {Style.Bouncer, Style.Soloist, Style.Engineer}),
    Secondary('P-19 Redeemer', Source.HM, SecondaryType.Pistol, {Style.Lawnmower, Style.Soloist, Style.Engineer}),
    Secondary('P-2 Peacemaker', Source.STOCK, SecondaryType.Pistol, {Style.Lawnmower, Style.Soloist, Style.Engineer}),
    Secondary('P-4 Senator', Source.SV, SecondaryType.Pistol, {Style.Juggernaut, Style.Soloist, Style.Sniper, Style.Sheriff}),
    Secondary('P-69 Veto', Source.ED, SecondaryType.Pistol, {Style.Trapper, Style.Bouncer, Style.Sheriff}),
    Secondary('P-92 Warrant', Source.FL, SecondaryType.Pistol, {Style.Tracker, Style.Bouncer}),
    Secondary('CQC-19 Stun Lance', Source.UL, SecondaryType.Melee, {Style.Brawler, Style.Sheriff, Style.Infiltrator, Style.Trapper}),
    Secondary('CQC-2 Saber', Source.MC, SecondaryType.Melee, {Style.Brawler, Style.Bouncer, Style.Sheriff, Style.Driver}),
    Secondary('CQC-30 Stun Baton', Source.UL, SecondaryType.Melee, {Style.Brawler, Style.Infiltrator, Style.Sheriff, Style.Trapper}),
    Secondary('CQC-42 Machete', Source.DUDE, SecondaryType.Melee, {Style.Brawler, Style.Bouncer, Style.Sheriff}),
    Secondary('CQC-5 Combat Hatchet', Source.SF, SecondaryType.Melee, {Style.Brawler, Style.Bouncer, Style.Sheriff}),
    Secondary('CQC-73 Entrenchment Tool', Source.ED, SecondaryType.Melee, {Style.Brawler, Style.Engineer}),
    Secondary('GP-20 Ultimatum', Source.SF, SecondaryType.Special, {Style.Artillerist, Style.Juggernaut, Style.Grenadier, Style.Demolitionist}),
    Secondary('GP-31 Grenade Pistol', Source.DD, SecondaryType.Special, {Style.Grenadier, Style.Demolitionist}),
    Secondary('LAS-58 Talon', Source.BJ, SecondaryType.Special, {Style.Optician, Style.Soloist, Style.Sniper}),
    Secondary('LAS-7 Dagger', Source.CE, SecondaryType.Special, {Style.Optician, Style.Soloist, Style.Medic, Style.Engineer}),
    Secondary('P-11 Stim Pistol', Source.CA, SecondaryType.Special, {Style.Medic, Style.Logistician}),
    Secondary('P-33 Missile Pistol', Source.EE, SecondaryType.Special, {Style.Tracker, Style.Juggernaut, Style.Demolitionist}),
    Secondary('P-35 Re-Educator', Source.RR, SecondaryType.Special, {Style.Fumigator, Style.Juggernaut, Style.Trapper, Style.Sniper}),
    Secondary('P-72 Crisper', Source.FF, SecondaryType.Special, {Style.Pyrotechnician, Style.Brawler, Style.Juggernaut}),
    Secondary('P-40K Bolt Pistol', Source.WH, SecondaryType.Special, {Style.Juggernaut, Style.Sheriff}),
    Secondary('PLAS-15 Loyalist', Source.TE, SecondaryType.Special, {Style.Cleanser, Style.Demolitionist, Style.Engineer, Style.Bouncer}),
    Secondary('SG-22 Bushwhacker', Source.VC, SecondaryType.Special, {Style.Brawler, Style.Lawnmower}),
    Throwable('G-10 Incendiary', Source.SV, ThrowableType.STD, {Style.Pyrotechnician, Style.Bouncer, Style.Grenadier, Style.Demolitionist}),
    Throwable('G-12 High Explosive', Source.STOCK, ThrowableType.STD, {Style.Grenadier, Style.Demolitionist, Style.Juggernaut}),
    Throwable('G-6 Frag', Source.HM, ThrowableType.STD, {Style.Grenadier, Style.Lawnmower, Style.Bouncer, Style.Demolitionist}),
    Throwable('G-7 Pineapple', Source.DUDE, ThrowableType.STD, {Style.Grenadier, Style.Lawnmower, Style.Bouncer, Style.Demolitionist}),
    Throwable('TED-63 Dynamite', Source.BJ, ThrowableType.STD, {Style.Grenadier, Style.Juggernaut, Style.Demolitionist, Style.Logistician, Style.Engineer}),
    Throwable('G-109 Urchin', Source.FL, ThrowableType.SL, {Style.Trapper, Style.Electrician, Style.Soloist, Style.Infiltrator, Style.Scout}),
    Throwable('G-123 Thermite', Source.DD, ThrowableType.SL, {Style.Juggernaut, Style.Demolitionist, Style.Grenadier, Style.Soloist, Style.Engineer}),
    Throwable('G-13 Incendiary Impact', Source.PP, ThrowableType.SL, {Style.Pyrotechnician, Style.Grenadier, Style.Sniper, Style.Scout}),
    Throwable('G-142 Pyrotech', Source.MC, ThrowableType.SL, {Style.Pyrotechnician, Style.Engineer, Style.Juggernaut, Style.Bouncer, Style.Lawnmower}),
    Throwable('G-16 Impact', Source.HM, ThrowableType.SL, {Style.Grenadier, Style.Juggernaut, Style.Sniper, Style.Scout}),
    Throwable('G-23 Stun', Source.CE, ThrowableType.SL, {Style.Trapper, Style.Electrician, Style.Soloist, Style.Lawnmower, Style.Scout, Style.Juggernaut, Style.Infiltrator}),
    Throwable('G-3 Smoke', Source.HM, ThrowableType.SL, {Style.Infiltrator, Style.Scout, Style.Engineer}),
    Throwable('G-31 Arc', Source.CG, ThrowableType.SL, {Style.Electrician, Style.Soloist, Style.Juggernaut, Style.Bouncer, Style.Lawnmower, Style.Trapper, Style.Grenadier}),
    Throwable('G-4 Gas', Source.CA, ThrowableType.SL, {Style.Trapper, Style.Fumigator, Style.Juggernaut, Style.Lawnmower, Style.Bouncer, Style.Demolitionist, Style.Grenadier}),
    Throwable('G-48 Giga Grenade', Source.ED, ThrowableType.SL, {Style.Juggernaut, Style.Demolitionist, Style.Soloist, Style.Artillerist}),
    Throwable('G-50 Seeker', Source.SF, ThrowableType.SL, {Style.Tracker, Style.Juggernaut, Style.Demolitionist, Style.Engineer, Style.Artillerist}),
    Throwable('G-89 Smokescreen', Source.RR, ThrowableType.SL, {Style.Infiltrator, Style.Scout, Style.Engineer}),
    Throwable('G/40-K Melta Mine', Source.WH, ThrowableType.SL, {Style.Engineer, Style.Juggernaut, Style.Trapper, Style.Demolitionist}),
    Throwable('G/SH-39 Shield', Source.SB, ThrowableType.SL, {Style.Engineer, Style.Soloist, Style.Sniper, Style.Logistician, Style.Survivalist}),
    Throwable('K-2 Throwing Knife', Source.VC, ThrowableType.SL, {Style.Infiltrator, Style.Brawler, Style.Bouncer}),
    Throwable('TM-1 Lure Mine', Source.RR, ThrowableType.SL, {Style.Infiltrator, Style.Engineer, Style.Trapper, Style.Juggernaut}),
    Stratagem('40-K Meltagun', Source.WH, StratagemSubtype.Weapon, {Style.Optician, Style.Juggernaut, Style.Brawler}),
    Stratagem('AC-8 Autocannon', Source.PAC, StratagemSubtype.BackpackWeapon, {Style.Juggernaut, Style.Grenadier, Style.Artillerist, Style.Logistician}),
    Stratagem('APW-1 Anti-Materiel Rifle', Source.PAC, StratagemSubtype.Weapon, {Style.Sniper, Style.Scout, Style.Spotter}),
    Stratagem('ARC-3 Arc Thrower', Source.EB, StratagemSubtype.Weapon, {Style.Brawler, Style.Juggernaut, Style.Electrician, Style.Trapper, Style.Soloist}),
    Stratagem('B/FLAM-80 Cremator', Source.ED, StratagemSubtype.BackpackWeapon, {Style.Pyrotechnician, Style.Juggernaut, Style.Brawler}),
    Stratagem('B/MD C4 Pack', Source.RR, StratagemSubtype.BackpackWeapon, {Style.Demolitionist, Style.Grenadier, Style.Juggernaut, Style.Infiltrator}),
    Stratagem('CQC-1 One True Flag', Source.MC, StratagemSubtype.Weapon, {Style.Brawler, Style.Soloist, Style.Trapper, Style.Sheriff}),
    Stratagem('CQC-20 Breaching Hammer', Source.SB, StratagemSubtype.Weapon, {Style.Brawler, Style.Soloist, Style.Juggernaut, Style.Demolitionist}),
    Stratagem('CQC-9 Defoliation Tool', Source.PC, StratagemSubtype.Weapon, {Style.Juggernaut, Style.Brawler, Style.Soloist, Style.Demolitionist}),
    Stratagem('EAT-17 Expendable Anti-Tank', Source.PAC, StratagemSubtype.Weapon, {Style.Juggernaut, Style.Scout, Style.Medic, Style.Logistician, Style.Sniper, Style.Demolitionist, Style.Spotter}),
    Stratagem('EAT-411 Leveller', Source.SB, StratagemSubtype.Weapon, {Style.Juggernaut, Style.Bouncer, Style.Lawnmower, Style.Demolitionist, Style.Soloist, Style.Scout}),
    Stratagem('EAT-700 Expendable Napalm', Source.DD, StratagemSubtype.Weapon, {Style.Juggernaut, Style.Pyrotechnician, Style.Lawnmower, Style.Scout, Style.Soloist}),
    Stratagem('FAF-14 Spear', Source.PAC, StratagemSubtype.Weapon, {Style.Logistician, Style.Tracker, Style.Juggernaut, Style.Sniper}),
    Stratagem('FLAM-40 Flamethrower', Source.PAC, StratagemSubtype.Weapon, {Style.Juggernaut, Style.Pyrotechnician, Style.Brawler, Style.Lawnmower, Style.Bouncer}),
    Stratagem('GL-21 Grenade Launcher', Source.EB, StratagemSubtype.Weapon, {Style.Grenadier, Style.Bouncer, Style.Lawnmower, Style.Demolitionist, Style.Artillerist}),
    Stratagem('GL-28 Belt-Fed Grenade Launcher', Source.SB, StratagemSubtype.BackpackWeapon, {Style.Grenadier, Style.Bouncer, Style.Lawnmower, Style.Demolitionist, Style.Artillerist, Style.Logistician}),
    Stratagem('GL-52 De-Escalator', Source.FL, StratagemSubtype.Weapon, {Style.Grenadier, Style.Artillerist, Style.Trapper, Style.Electrician}),
    Stratagem('GR-8 Recoilless Rifle', Source.PAC, StratagemSubtype.BackpackWeapon, {Style.Artillerist, Style.Juggernaut, Style.Logistician, Style.Sniper, Style.Demolitionist}),
    Stratagem('LAS-98 Laser Cannon', Source.EB, StratagemSubtype.Weapon, {Style.Optician, Style.Sniper, Style.Juggernaut, Style.Soloist, Style.Bouncer, Style.Spotter}),
    Stratagem('LAS-99 Quasar Cannon', Source.EB, StratagemSubtype.Weapon, {Style.Optician, Style.Juggernaut, Style.Demolitionist, Style.Soloist, Style.Spotter}),
    Stratagem('M-1000 Maxigun', Source.PC, StratagemSubtype.BackpackWeapon, {Style.Bouncer, Style.Logistician, Style.Lawnmower}),
    Stratagem('M-105 Stalwart', Source.PAC, StratagemSubtype.Weapon, {Style.Lawnmower, Style.Logistician, Style.Soloist}),
    Stratagem('MG-206 Heavy Machine Gun', Source.PAC, StratagemSubtype.Weapon, {Style.Lawnmower, Style.Logistician, Style.Soloist, Style.Juggernaut, Style.Bouncer}),
    Stratagem('MG-43 Machine Gun', Source.STOCK, StratagemSubtype.Weapon, {Style.Lawnmower, Style.Bouncer, Style.Logistician, Style.Soloist}),
    Stratagem('MGX-42 Bullet Storm', Source.EE, StratagemSubtype.Weapon, {Style.Lawnmower, Style.Logistician, Style.Soloist, Style.Scout}),
    Stratagem('MLS-4X Commando', Source.PAC, StratagemSubtype.Weapon, {Style.Artillerist, Style.Tracker, Style.Juggernaut, Style.Demolitionist}),
    Stratagem('MS-11 Solo Silo', Source.DUDE, StratagemSubtype.Weapon, {Style.Artillerist, Style.Tracker, Style.Sniper, Style.Juggernaut, Style.Demolitionist}),
    Stratagem('PLAS-45 Epoch', Source.CG, StratagemSubtype.Weapon, {Style.Medic, Style.Engineer, Style.Cleanser, Style.Scout, Style.Juggernaut, Style.Bouncer}),
    Stratagem('RL-77 Airburst Rocket Launcher', Source.PAC, StratagemSubtype.BackpackWeapon, {Style.Artillerist, Style.Scout, Style.Sniper, Style.Lawnmower, Style.Bouncer, Style.Logistician}),
    Stratagem('RS-422 Railgun', Source.PAC, StratagemSubtype.Weapon, {Style.Sniper, Style.Juggernaut, Style.Infiltrator}),
    Stratagem('S-11 Speargun', Source.DUDE, StratagemSubtype.Weapon, {Style.Fumigator, Style.Trapper, Style.Juggernaut, Style.Demolitionist}),
    Stratagem('StA-X3 W.A.S.P. Launcher', Source.KZ, StratagemSubtype.BackpackWeapon, {Style.Artillerist, Style.Juggernaut, Style.Sniper, Style.Demolitionist}),
    Stratagem('TX-41 Sterilizer', Source.CA, StratagemSubtype.Weapon, {Style.Trapper, Style.Fumigator, Style.Brawler, Style.Juggernaut, Style.Lawnmower, Style.Bouncer}),
    Stratagem('Orbital 120mm HE Barrage', Source.OC, StratagemSubtype.Orbital, {Style.Spotter, Style.Demolitionist, Style.Artillerist, Style.Juggernaut, Style.Bouncer, Style.Lawnmower, Style.Sniper}),
    Stratagem('Orbital 380mm HE Barrage', Source.OC, StratagemSubtype.Orbital, {Style.Spotter, Style.Demolitionist, Style.Artillerist, Style.Juggernaut, Style.Bouncer, Style.Lawnmower, Style.Scout}),
    Stratagem('Walking Barrage', Source.OC, StratagemSubtype.Orbital, {Style.Spotter, Style.Artillerist, Style.Juggernaut, Style.Bouncer, Style.Lawnmower, Style.Soloist}),
    Stratagem('Orbital Airburst Strike', Source.OC, StratagemSubtype.Orbital, {Style.Spotter, Style.Lawnmower, Style.Bouncer, Style.Scout, Style.Soloist}),
    Stratagem('Orbital EMS Strike', Source.BR, StratagemSubtype.Orbital, {Style.Spotter, Style.Trapper, Style.Artillerist, Style.Soloist, Style.Infiltrator}),
    Stratagem('Orbital Gas Strike', Source.BR, StratagemSubtype.Orbital, {Style.Spotter, Style.Trapper, Style.Fumigator, Style.Artillerist, Style.Soloist}),
    Stratagem('Orbital Gatling Barrage', Source.OC, StratagemSubtype.Orbital, {Style.Spotter, Style.Scout, Style.Artillerist, Style.Medic, Style.Engineer, Style.Soloist}),
    Stratagem('Orbital Laser', Source.OC, StratagemSubtype.Orbital, {Style.Spotter, Style.Optician, Style.Juggernaut, Style.Demolitionist, Style.Pyrotechnician}),
    Stratagem('Orbital Napalm Barrage', Source.OC, StratagemSubtype.Orbital, {Style.Spotter, Style.Pyrotechnician, Style.Juggernaut, Style.Lawnmower, Style.Bouncer, Style.Artillerist, Style.Soloist}),
    Stratagem('Orbital Precision Strike', Source.STOCK, StratagemSubtype.Orbital, {Style.Spotter, Style.Medic, Style.Engineer, Style.Artillerist, Style.Demolitionist}),
    Stratagem('Orbital Railcannon Strike', Source.OC, StratagemSubtype.Orbital, {Style.Spotter, Style.Artillerist, Style.Juggernaut, Style.Sniper, Style.Tracker}),
    Stratagem('Orbital Smoke Strike', Source.BR, StratagemSubtype.Orbital, {Style.Infiltrator, Style.Spotter, Style.Engineer, Style.Medic}),
    Stratagem('Eagle 110mm Rocket Pods', Source.HG, StratagemSubtype.Eagle, {Style.Juggernaut, Style.Tracker, Style.Spotter, Style.Demolitionist}),
    Stratagem('Eagle 500kg Bomb', Source.HG, StratagemSubtype.Eagle, {Style.Demolitionist, Style.Spotter, Style.Juggernaut}),
    Stratagem('Eagle Airstrike', Source.HG, StratagemSubtype.Eagle, {Style.Demolitionist, Style.Spotter, Style.Juggernaut, Style.Bouncer, Style.Lawnmower}),
    Stratagem('Eagle Cluster Bomb', Source.HG, StratagemSubtype.Eagle, {Style.Bouncer, Style.Lawnmower, Style.Spotter}),
    Stratagem('Eagle Gas Airstrike', Source.EV_CH, StratagemSubtype.Eagle, {Style.Fumigator, Style.Spotter, Style.Trapper, Style.Lawnmower, Style.Juggernaut, Style.Bouncer, Style.Scout}),
    Stratagem('Eagle Napalm Airstrike', Source.HG, StratagemSubtype.Eagle, {Style.Pyrotechnician, Style.Spotter, Style.Juggernaut, Style.Bouncer, Style.Lawnmower}),
    Stratagem('Eagle Smoke Strike', Source.HG, StratagemSubtype.Eagle, {Style.Infiltrator, Style.Scout, Style.Engineer, Style.Medic, Style.Spotter}),
    Stratagem('Eagle Strafing Run', Source.HG, StratagemSubtype.Eagle, {Style.Spotter, Style.Demolitionist, Style.Juggernaut, Style.Bouncer, Style.Lawnmower}),
    Stratagem('E/AT-12 Anti-Tank Emplacement', Source.UL, StratagemSubtype.Emplacement, {Style.Engineer, Style.Artillerist, Style.Juggernaut}),
    Stratagem('E/GL-21 Grenadier Battlement', Source.BR, StratagemSubtype.Emplacement, {Style.Engineer, Style.Grenadier, Style.Artillerist, Style.Juggernaut, Style.Lawnmower, Style.Bouncer}),
    Stratagem('E/MG-101 HMG Emplacement', Source.BR, StratagemSubtype.Emplacement, {Style.Engineer, Style.Juggernaut, Style.Bouncer, Style.Lawnmower, Style.Artillerist}),
    Stratagem('FX-12 Shield Generator Relay', Source.BR, StratagemSubtype.Emplacement, {Style.Engineer, Style.Medic, Style.Logistician, Style.Survivalist, Style.Sniper}),
    Stratagem('MD-17 Anti-Tank Mines', Source.EB, StratagemSubtype.Minefield, {Style.Trapper, Style.Demolitionist, Style.Juggernaut}),
    Stratagem('MD-6 Anti-Personnel Minefield', Source.EB, StratagemSubtype.Minefield, {Style.Trapper, Style.Demolitionist, Style.Bouncer, Style.Lawnmower}),
    Stratagem('MD-8 Gas Mines', Source.EB, StratagemSubtype.Minefield, {Style.Trapper, Style.Fumigator}),
    Stratagem('MD-I4 Incendiary Mines', Source.EB, StratagemSubtype.Minefield, {Style.Trapper, Style.Pyrotechnician}),
    Stratagem('A/AC-8 Autocannon Sentry', Source.RW, StratagemSubtype.Sentry, {Style.Engineer, Style.Artillerist}),
    Stratagem('A/ARC-3 Tesla Tower', Source.BR, StratagemSubtype.Sentry, {Style.Engineer, Style.Electrician, Style.Trapper}),
    Stratagem('A/FLAM-40 Flame Sentry', Source.UL, StratagemSubtype.Sentry, {Style.Engineer, Style.Pyrotechnician, Style.Sheriff, Style.Scout}),
    Stratagem('A/G-16 Gatling Sentry', Source.RW, StratagemSubtype.Sentry, {Style.Engineer, Style.Medic, Style.Scout}),
    Stratagem('A/GM-17 Gas Mortar Sentry', Source.ED, StratagemSubtype.Sentry, {Style.Engineer, Style.Artillerist, Style.Fumigator, Style.Tracker}),
    Stratagem('A/LAS-98 Laser Sentry', Source.CG, StratagemSubtype.Sentry, {Style.Engineer, Style.Optician}),
    Stratagem('A/M-12 Mortar Sentry', Source.RW, StratagemSubtype.Sentry, {Style.Engineer, Style.Artillerist}),
    Stratagem('A/M-23 EMS Mortar Sentry', Source.RW, StratagemSubtype.Sentry, {Style.Engineer, Style.Artillerist, Style.Trapper}),
    Stratagem('A/MG-43 Machine Gun Sentry', Source.RW, StratagemSubtype.Sentry, {Style.Engineer, Style.Medic, Style.Scout}),
    Stratagem('A/MLS-4X Rocket Sentry', Source.RW, StratagemSubtype.Sentry, {Style.Engineer, Style.Tracker, Style.Sniper, Style.Artillerist}),
    Stratagem('AX/AR-23 Guard Dog', Source.EB, StratagemSubtype.Backpack, {Style.Soloist, Style.Engineer, Style.Scout, Style.Sheriff, Style.Survivalist}),
    Stratagem('AX/ARC-3 K-9', Source.FL, StratagemSubtype.Backpack, {Style.Soloist, Style.Engineer, Style.Electrician, Style.Trapper}),
    Stratagem('AX/FLAM-75 Hot Dog', Source.PC, StratagemSubtype.Backpack, {Style.Soloist, Style.Pyrotechnician, Style.Engineer}),
    Stratagem('AX/LAS-5 Rover', Source.EB, StratagemSubtype.Backpack, {Style.Soloist, Style.Optician, Style.Engineer, Style.Scout, Style.Survivalist}),
    Stratagem('AX/TX-13 Dog Breath', Source.CA, StratagemSubtype.Backpack, {Style.Soloist, Style.Fumigator, Style.Trapper, Style.Engineer, Style.Sniper}),
    Stratagem('B-1 Supply Pack', Source.EB, StratagemSubtype.Backpack, {Style.Soloist, Style.Logistician, Style.Medic, Style.Survivalist}),
    Stratagem('B-100 Portable Hellbomb', Source.SF, StratagemSubtype.Backpack, {Style.Demolitionist, Style.Engineer, Style.Soloist}),
    Stratagem('LIFT-182 Warp Pack', Source.CG, StratagemSubtype.Backpack, {Style.Scout, Style.Infiltrator, Style.Sniper, Style.Medic, Style.Survivalist, Style.Driver}),
    Stratagem('LIFT-850 Jump Pack', Source.HG, StratagemSubtype.Backpack, {Style.Scout, Style.Infiltrator, Style.Grenadier, Style.Survivalist, Style.Pilot}),
    Stratagem('LIFT-860 Hover Pack', Source.BJ, StratagemSubtype.Backpack, {Style.Soloist, Style.Pyrotechnician, Style.Fumigator, Style.Grenadier, Style.Pilot, Style.Driver}),
    Stratagem('SH-20 Ballistic Shield Backpack', Source.EB, StratagemSubtype.Backpack, {Style.Sheriff, Style.Engineer, Style.Medic, Style.Survivalist}),
    Stratagem('SH-32 Shield Generator Pack', Source.EB, StratagemSubtype.Backpack, {Style.Medic, Style.Engineer, Style.Survivalist, Style.Driver, Style.Pilot}),
    Stratagem('SH-51 Directional Shield', Source.UL, StratagemSubtype.Backpack, {Style.Medic, Style.Engineer, Style.Survivalist, Style.Soloist}),
    Stratagem('EXO-45 Patriot Exosuit', Source.RW, StratagemSubtype.Exosuit, {Style.Pilot, Style.Engineer}),
    Stratagem('EXO-49 Emancipator Exosuit', Source.RW, StratagemSubtype.Exosuit, {Style.Pilot, Style.Artillerist}),
    Stratagem('EXO-51 Lumberer Exosuit', Source.EE, StratagemSubtype.Exosuit, {Style.Pilot, Style.Juggernaut, Style.Pyrotechnician}),
    Stratagem('EXO-55 Breakthrough Exosuit', Source.EE, StratagemSubtype.Exosuit, {Style.Pilot, Style.Artillerist, Style.Sheriff, Style.Engineer}),
    Stratagem('M-102 Gunner FRV', Source.HG, StratagemSubtype.FRV, {Style.Driver, Style.Juggernaut}),
    Stratagem('M-103 Supply FRV', Source.EV_CT, StratagemSubtype.FRV, {Style.Driver, Style.Logistician}),
    # Stratagem('M-104 Incinerator FRV', Source.EV, StratagemSubtype.FRV, {Style.Driver, Style.Pyrotechnician}),
    Stratagem('TD-220 Bastion MK XVI', Source.HG, StratagemSubtype.Tank, {Style.Driver}),
    Booster('Hellpod Space Optimization', Source.HM, {Style.Medic, Style.Logistician, Style.Soloist, Style.Engineer, Style.Driver}),
    Booster('Vitality Enhancement', Source.HM, {Style.Medic, Style.Survivalist, Style.Cleanser, Style.Pyrotechnician, Style.Demolitionist}),
    Booster('UAV Recon Booster', Source.HM, {Style.Scout, Style.Sniper, Style.Driver, Style.Pilot, Style.Tracker, Style.Sheriff}),
    Booster('Stamina Enhancement', Source.HM, {Style.Scout, Style.Infiltrator, Style.Trapper, Style.Brawler, Style.Spotter}),
    Booster('Muscle Enhancement', Source.HM, {Style.Scout, Style.Trapper, Style.Grenadier, Style.Demolitionist}),
    Booster('Increased Reinforcement Budget', Source.HM, {Style.Driver, Style.Pilot, Style.Demolitionist, Style.Trapper, Style.Fumigator}),
    Booster('Flexible Reinforcement Budget', Source.SV, {Style.Driver, Style.Pilot, Style.Demolitionist, Style.Trapper, Style.Pyrotechnician}),
    Booster('Localization Confusion', Source.CE, {Style.Scout, Style.Sniper, Style.Infiltrator}),
    Booster('Expert Extraction Pilot', Source.DD, {Style.Pilot, Style.Engineer, Style.Infiltrator, Style.Tracker, Style.Sheriff}),
    Booster('Motivational Shocks', Source.PP, {Style.Trapper, Style.Electrician, Style.Brawler, Style.Survivalist}),
    Booster('Experimental Infusion', Source.VC, {Style.Medic, Style.Scout, Style.Survivalist, Style.Brawler, Style.Sheriff}),
    Booster('Firebomb Hellpods', Source.FF, {Style.Pyrotechnician, Style.Demolitionist, Style.Spotter, Style.Tracker}),
    Booster('Dead Sprint', Source.TE, {Style.Scout, Style.Sniper, Style.Soloist, Style.Spotter, Style.Pilot, Style.Driver}),
    Booster('Armed Resupply Pods', Source.UL, {Style.Sheriff, Style.Logistician, Style.Engineer, Style.Spotter}),
    Booster('Sample Extricator', Source.BJ, {Style.Pilot, Style.Soloist, Style.Logistician}),
    Booster('Sample Scanner', Source.MC, {Style.Driver, Style.Scout, Style.Infiltrator}),
    Booster('Stun Pods', Source.FL, {Style.Pilot, Style.Trapper, Style.Spotter, Style.Tracker}),
    Booster('Concealed Insertion', Source.RR, {Style.Pilot, Style.Driver, Style.Infiltrator, Style.Scout, Style.Spotter}),
]


class Inventory:
    def __init__(self, items: Iterable[EquipmentItem] | None = None):
        self.all_items = set(items or ())
        self._arrange_by_slot()

    def __len__(self):
        return len(self.all_items)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.all_items!r})'

    def __iter__(self):
        yield from self.all_items

    def __add__(self, other: Self) -> Self:
        return self.__class__(self.all_items | other.all_items)

    def __sub__(self, other: Self) -> Self:
        return self.__class__(self.all_items - other.all_items)

    def __or__(self, other: Inventory) -> Self:
        equipment_union = self.all_items | other.all_items
        return self.__class__(equipment_union)

    def __ior__(self, other: Self):
        self.update(other)

    def __and__(self, other: Inventory) -> Self:
        equipment_intersection = self.all_items & other.all_items
        return self.__class__(equipment_intersection)

    def slot(self, slot: Slot) -> set[EquipmentItem]:
        match slot:
            case Slot.Primary:
                items = self.primary
            case Slot.Secondary:
                items = self.secondary
            case Slot.Throwable:
                items = self.throwable
            case Slot.Booster:
                items = self.booster
            case Slot.Armor:
                items = self.armor
            case _:
                items = self.stratagem
        return items

    def _arrange_by_slot(self):
        self.primary: set[Primary] = self.filter_items(by_slot=Slot.Primary)
        self.secondary: set[Secondary] = self.filter_items(by_slot=Slot.Secondary)
        self.throwable: set[Throwable] = self.filter_items(by_slot=Slot.Throwable)
        self.stratagem: set[Stratagem] = self.filter_items(by_slot=Slot.Stratagem)
        self.booster: set[Booster] = self.filter_items(by_slot=Slot.Booster)
        self.armor: set[Armor] = self.filter_items(by_slot=Slot.Armor)

    def filter_items(self, by_slot: Slot | None = None, by_source: Source | None = None, by_style: Style | None = None):
        def predicate(item: EquipmentItem) -> bool:
            return ((item.source is by_source if by_source is not None else True)
                    and (item.slot is by_slot if by_slot is not None else True)
                    and (by_style in item.styles if by_style is not None else True))
        return set(filter(predicate, self.all_items))

    def make_subset(self, sources: set[Source] | None = None,
                    designations: set[str] | None = None,
                    names: set[str] | None = None) -> Self:
        items = set()
        if sources:
            items.update(item for item in self.all_items if item.source in sources)
        if designations:
            items.update(self.lookup_batch(list(designations), by_name=False))
        if names:
            items.update(self.lookup_batch(list(names), by_name=True))
        return self.__class__(items)

    def filter_armor(self, by_styles: set[Style] | None = None,
                     by_passives: set[Passive] | None = None):
        def predicate(item: Armor) -> bool:
            return bool(by_styles and (item.styles & by_styles)
                        or (by_passives and (item.passive in by_passives)))
        return set(filter(predicate, self.armor))

    def filter_stratagems(self, by_types: Iterable[StratagemType] | None = None,
                          by_subtype: StratagemSubtype | None = None) -> set[Stratagem]:
        if by_types is not None:
            wanted = set(by_types)
            def pred(strat: Stratagem) -> bool:
                return strat.type in wanted
        elif by_subtype is not None:
            # noinspection unsupported-operator
            def pred(strat: Stratagem) -> bool:
                return by_subtype in strat.subtype
        else:
            return set()
        return set(filter(pred, self.stratagem))

    def update(self, other: Self):
        self.all_items.update(other.all_items if isinstance(other, self.__class__) else other)
        self._arrange_by_slot()

    def add(self, equipment: EquipmentItem | list[EquipmentItem]):
        if isinstance(equipment, list):
            self.all_items.update(equipment)
        else:
            self.all_items.add(equipment)
        self._arrange_by_slot()

    def remove(self, by_designation: str | list[str]):
        if isinstance(by_designation, str):
            by_designation = [by_designation]
        any_removed = False
        for d in by_designation:
            if found := self.lookup(d):
                self.all_items.discard(found)
                any_removed = True
        if any_removed:
            self._arrange_by_slot()

    def lookup(self, by_designation: str | None = None, by_name: str | None = None) -> EquipmentItem | None:
        if by_name:
            cf = by_name.casefold()
        elif by_designation:
            cf = by_designation.casefold()
        else:
            return None
        for item in self.all_items:
            if by_name and item.name.casefold() == cf:
                return item
            if by_designation and item.designation.casefold() == cf:
                return item
            if item.shortname.casefold().startswith(cf):
                return item
        return None

    def lookup_batch(self, keys: list[str], by_name: bool = True) -> list[EquipmentItem]:
        out = []
        for d in keys:
            if found := self.lookup(**{('by_name' if by_name else 'by_designation'): d}):
                out.append(found)
        return out

    def ready(self):
        primary = len(self.primary) >= 1
        secondary = len(self.secondary) >= 1
        throwable = len(self.throwable) >= 1
        stratagems = len(self.filter_stratagems({StratagemType.Defensive, StratagemType.Offensive})) >= 4
        armor = len(self.armor) >= 1
        booster = len(self.booster) >= 1
        return primary and secondary and throwable and stratagems and armor and booster


Everything = Inventory(_Equipment)
BySource = {src: Inventory(Everything.filter_items(by_source=src)) for src in Source}
ByStyle = {style: Inventory(Everything.filter_items(by_style=style)) for style in Style}
