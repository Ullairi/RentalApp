from enum import StrEnum


class Gender(StrEnum):
    """User gender"""
    male = "Male"
    female = "Female"

    @classmethod
    def choices(cls):
        return [(gender.name, gender.value) for gender in cls]


class UserRole(StrEnum):
    """Role of a user in system"""
    owner = "Owner"
    tenant = "Tenant"
    admin = "Admin"

    @classmethod
    def choices(cls):
        return [(role.name, role.value) for role in cls]


class HouseType(StrEnum):
    """Type of the house presented in listing"""
    house = "House"
    room = "Room"
    apartment = "Apartment"
    studio = "Studio"

    @classmethod
    def choices(cls):
        return [(house_type.name, house_type.value) for house_type in cls]


class AmenityCategory(StrEnum):
    """Category of house comfortability"""
    basic = "Basic"
    comfort = "Comfort"
    premium = "Premium"

    @classmethod
    def choices(cls):
        return [(amen_categ.name, amen_categ.value) for amen_categ in cls]


class BookingStatus(StrEnum):
    """status of booking"""
    pending = "Pending"
    rejected = "Rejected"
    confirmed = "Confirmed"
    cancelled = "Cancelled"
    completed = "Completed"

    @classmethod
    def choices(cls):
        return [(book_stat.name, book_stat.value) for book_stat in cls]


class VerificationStatus(StrEnum):
    """Verification status"""
    pending = "Pending"
    approved = "Approved"
    rejected = "Rejected"

    @classmethod
    def choices(cls):
        return [(verif_stat.name, verif_stat.value) for verif_stat in cls]

class Land(StrEnum):
    """German federal states"""
    baden_wurttemberg = "Baden-Württemberg"
    bayern = "Bayern"
    berlin = "Berlin"
    brandenburg = "Brandenburg"
    bremen = "Bremen"
    hamburg = "Hamburg"
    hessen = "Hessen"
    mecklenburg_vorpommern = "Mecklenburg-Vorpommern"
    niedersachsen = "Niedersachsen"
    nordrhein_westfalen = "Nordrhein-Westfalen"
    rheinland_pfalz = "Rheinland-Pfalz"
    saarland = "Saarland"
    sachsen = "Sachsen"
    sachsen_anhalt = "Sachsen-Anhalt"
    schleswig_holstein = "Schleswig-Holstein"
    thuringen = "Thüringen"

    @classmethod
    def choices(cls):
        return [(land.name, land.value) for land in cls]