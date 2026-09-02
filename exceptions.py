class RandomizerError(Exception):
    pass


class CatalogError(RandomizerError):
    pass


class RegistrationError(RandomizerError):
    pass


class UserNotRegistered(RegistrationError):
    pass


class InvalidSquad(RegistrationError):
    pass


class UnknownEquipment(CatalogError):
    pass


class UnknownSlot(CatalogError):
    pass


class StratagemSubtypeMismatch(CatalogError):
    pass