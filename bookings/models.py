from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

from core.validators import validate_future_date
from core.mixins import TimestampMixin
from core.enums import BookingStatus


class Booking(TimestampMixin):
    """Booking model"""
    listing = models.ForeignKey('listings.Listing', on_delete=models.CASCADE, related_name='bookings')
    tenant = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='bookings')
    stayers = models.PositiveIntegerField()
    check_in = models.DateField(validators=[validate_future_date])
    check_out = models.DateField(validators=[validate_future_date])
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='Total price (€)')
    book_status = models.CharField(
        max_length=20,
        choices=BookingStatus.choices(),
        default=BookingStatus.pending.name
    )

    class Meta:
        db_table = 'bookings'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['listing']),
            models.Index(fields=['tenant']),
            models.Index(fields=['check_in']),
            models.Index(fields=['book_status']),
        ]

    def __str__(self):
        return f'Booking {self.id} - {self.listing.title} ({self.book_status})'

    def clean(self):
        """Check-in/check-out and stayers count validation"""
        if self.check_out and self.check_in and self.check_out <= self.check_in:
            raise ValidationError('Check-out must be after check-in date')
        if self.listing and self.stayers and self.stayers > self.listing.max_stayers:
            raise ValidationError(f'Maximum {self.listing.max_stayers} stayers allowed')

    def save(self, *args, **kwargs):
        """Calculation of total price beofre saving booking"""
        if self.total_price is None and self.listing and self.check_in and self.check_out:
            nights = (self.check_out - self.check_in).days
            self.total_price = self.listing.price_per_night * nights
        super().save(*args, **kwargs)

    @property
    def nights_to_stay(self):
        """Night between check-in/check-out"""
        if self.check_out and self.check_in:
            return (self.check_out - self.check_in).days
        return 0

    @property
    def cancelation(self):
        """
        Booking cancelation
        Only when status pending or confirmed
        Only if check-in date in the future
        """
        return (
            self.book_status in [BookingStatus.pending.name, BookingStatus.confirmed.name]
            and self.check_in > timezone.now().date()
        )


class BookingStatusHistory(TimestampMixin):
    """Stores all booking status history"""
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='status_history')
    history_status = models.CharField(max_length=20, choices=BookingStatus.choices())
    comment = models.TextField(blank=True)
    changed_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'booking_status_history'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.booking.id} - {self.history_status}'