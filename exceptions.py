class RandomizerError(Exception):
    pass


class CatalogError(RandomizerError):
    pass


class UnknownEquipment(CatalogError):
    pass


class UnknownSlot(CatalogError):
    pass


class StratagemSubtypeMismatch(CatalogError):
    pass