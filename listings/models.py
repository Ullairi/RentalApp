from django.db import models
from core.mixins import TimestampMixin
from core.enums import HouseType, AmenityCategory, Land
from core.validators import validate_positive_price, validate_positive_number, validate_no_digits, validate_postal_code, \
    validate_apartment_number
from django.db.models import Avg


class Amenity(TimestampMixin):
    """Amenity model for listings"""
    name = models.CharField(max_length=70, unique=True)
    category = models.CharField(max_length=20, choices=AmenityCategory.choices())
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'amenities'
        verbose_name = 'Amenity'
        verbose_name_plural = 'Amenities'
        ordering = ['category', 'name']
        indexes = [models.Index(fields=['category'])]

    def __str__(self):
        return f'{self.name} ({self.category})'

class Address(TimestampMixin):
    """Model for listing address"""
    country = models.CharField(max_length=70, default='Germany')
    city = models.CharField(max_length=70, validators=[validate_no_digits])
    land = models.CharField(max_length=30, choices=Land.choices())
    street = models.CharField(max_length=50, validators=[validate_no_digits])
    house_number = models.CharField(max_length=10)
    apartment_number = models.CharField(max_length=5, blank=True, validators=[validate_apartment_number])
    postal_code = models.CharField(max_length=5, validators=[validate_postal_code])

    class Meta:
        db_table = 'addresses'
        verbose_name = 'Address'
        verbose_name_plural = "Addresses"
        unique_together = ['street', 'house_number', 'apartment_number', 'city', 'postal_code']
        indexes = [
            models.Index(fields=['city']),
            models.Index(fields=['postal_code']),
        ]

    def __str__(self):
        addr = f'{self.street} {self.house_number}'
        if self.apartment_number:
            addr += f', Apartment {self.apartment_number}'
        return f'{addr}, {self.city}, {self.postal_code}'

    @property
    def full_address(self):
        parts = [f'{self.street} {self.house_number}']
        if self.apartment_number:
            parts[0] += f', Apartment {self.apartment_number}'
        parts.append(self.city)
        if self.land:
            parts.append(self.land)
        parts.append(self.postal_code)
        parts.append(self.country)
        return ', '.join(parts)

class Listing(TimestampMixin):
    """Model for listings creation"""
    title = models.CharField(max_length=50)
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='listings')
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    views_count = models.PositiveIntegerField(default=0)
    address = models.OneToOneField(Address, on_delete=models.CASCADE, related_name='listing')
    house_type = models.CharField(max_length=20, choices=HouseType.choices())
    amenities = models.ManyToManyField(Amenity, related_name='listings', blank=True)
    max_stayers = models.PositiveIntegerField(validators=[validate_positive_number])
    bedrooms = models.PositiveIntegerField(validators=[validate_positive_number])
    bathrooms = models.PositiveIntegerField(validators=[validate_positive_number])
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2, validators=[validate_positive_price], verbose_name='Price per night (€)')

    class Meta:
        db_table = 'listings'
        verbose_name = 'Listing'
        verbose_name_plural = 'Listings'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner']),
            models.Index(fields=['is_active']),
            models.Index(fields=['house_type']),
            models.Index(fields=['price_per_night']),
        ]

    def __str__(self):
        return f'{self.title} - {self.address.city}'

    @property
    def avg_rating(self):
        result = self.reviews.aggregate(avg=Avg('rating'))
        return result['avg']

class ListingImg(TimestampMixin):
    """Model for images attached to listings"""
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='images')
    img = models.ImageField(upload_to='listings/%Y/%m/%d/')
    main = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.main:
            ListingImg.objects.filter(listing=self.listing, main=True).exclude(pk=self.pk).update(main=False)
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'listing_imgs'
        verbose_name = 'Listing image'
        verbose_name_plural = 'Listing images'
        ordering = ['-main', '-created_at']

    def __str__(self):
        return f'Image #{self.pk}'

class SearchHistory(models.Model):
    """Model for search history"""
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='search_history',
        null=True, blank=True
    )
    query = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'search_history'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['query']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f'{self.query} ({self.user or "anonymous"})'


class ViewHistory(models.Model):
    """Listing search history"""
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='view_history',
        null=True, blank=True
    )
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='view_history'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'view_history'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['listing']),
        ]

    def __str__(self):
        return f'{self.user or "anonymous"} - {self.listing_id}'