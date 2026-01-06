import os
import random
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RentalApp.settings')

import django
django.setup()

import factory
from factory import fuzzy
from faker import Faker
from django.contrib.auth.hashers import make_password
from django.utils import timezone

from users.models import User, Favorite
from listings.models import Address, Amenity, Listing
from bookings.models import Booking, BookingStatusHistory
from reviews.models import Review
from core.enums import UserRole, Gender, HouseType, BookingStatus, Land

faker_ = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('username',)

    username = factory.LazyAttribute(lambda _: faker_.unique.user_name())
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@gmail.com")
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    role = factory.LazyFunction(lambda: random.choice([UserRole.tenant.name, UserRole.owner.name]))
    gender = factory.LazyFunction(lambda: random.choice([Gender.male.name, Gender.female.name]))
    birth_date = factory.Faker('date_of_birth', minimum_age=18, maximum_age=65)
    phone = factory.LazyAttribute(lambda _: f"+49{faker_.msisdn()[4:15]}")
    is_staff = False
    is_active = True
    password = factory.LazyFunction(lambda: make_password("TestPass123!"))


class AddressFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Address

    country = 'Germany'
    city = factory.Faker('city')
    land = factory.LazyFunction(lambda: random.choice([land.name for land in Land]))
    street = factory.Faker('street_name')
    house_number = factory.LazyAttribute(lambda _: str(random.randint(1, 150)))
    apartment_number = factory.LazyAttribute(lambda _: str(random.randint(1, 50)) if random.random() > 0.3 else '')
    postal_code = factory.LazyAttribute(lambda _: str(random.randint(10000, 99999)))


class ListingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Listing

    title = factory.Faker('sentence', nb_words=4)
    description = factory.Faker('paragraph', nb_sentences=5)
    address = factory.SubFactory(AddressFactory)
    owner = factory.SubFactory(UserFactory, role=UserRole.owner.name)
    house_type = factory.LazyFunction(lambda: random.choice([ht.name for ht in HouseType]))
    bedrooms = fuzzy.FuzzyInteger(1, 5)
    bathrooms = fuzzy.FuzzyInteger(1, 3)
    max_stayers = factory.LazyAttribute(lambda obj: obj.bedrooms * 2)
    price_per_night = fuzzy.FuzzyDecimal(30, 500, precision=2)
    is_active = True
    views_count = fuzzy.FuzzyInteger(0, 200)


class BookingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Booking

    listing = factory.SubFactory(ListingFactory)
    tenant = factory.SubFactory(UserFactory, role=UserRole.tenant.name)
    stayers = factory.LazyAttribute(lambda obj: random.randint(1, obj.listing.max_stayers))
    check_in = factory.LazyFunction(lambda: timezone.now().date() - timedelta(days=random.randint(30, 60)))
    check_out = factory.LazyAttribute(lambda obj: obj.check_in + timedelta(days=random.randint(2, 14)))
    book_status = BookingStatus.completed.name


class ReviewFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Review

    author = factory.SubFactory(UserFactory, role=UserRole.tenant.name)
    listing = factory.SubFactory(ListingFactory)
    booking = factory.SubFactory(BookingFactory)
    rating = fuzzy.FuzzyInteger(3, 5)
    comment = factory.Faker('text', max_nb_chars=600)


if __name__ == "__main__":
    print("Creating test data...")

    for name, cat in [('WiFi', 'basic'), ('Kitchen', 'comfort'), ('Pool', 'premium'), ('Parking', 'comfort')]:
        Amenity.objects.get_or_create(name=name, defaults={'category': cat})

    owners = [UserFactory(role=UserRole.owner.name) for _ in range(5)]
    tenants = [UserFactory(role=UserRole.tenant.name) for _ in range(10)]

    listings = [ListingFactory(owner=random.choice(owners)) for _ in range(15)]

    bookings = [BookingFactory(listing=random.choice(listings), tenant=random.choice(tenants)) for _ in range(20)]

    for b in bookings[:10]:
        if not Review.objects.filter(author=b.tenant, listing=b.listing).exists():
            Review.objects.create(
                author=b.tenant,
                listing=b.listing,
                booking=b,
                rating=random.randint(3, 5),
                comment=faker_.paragraph()
            )

    print("Done!")
    print(f"Login: {tenants[0].email} / TestPass123!")