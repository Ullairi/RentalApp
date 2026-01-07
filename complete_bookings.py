import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RentalApp.settings')
django.setup()

from django.utils import timezone
from bookings.models import Booking, BookingStatusHistory


def complete_bookings():
    today = timezone.now().date()

    bookings = Booking.objects.filter(
        book_status='confirmed',
        check_out__lt=today
    )

    count = 0
    for booking in bookings:
        booking.book_status = 'completed'
        booking.save()

        BookingStatusHistory.objects.create(
            booking=booking,
            history_status='completed',
            comment='Automatically completed after check-out date'
        )
        count += 1

    print(f'Completed {count} bookings')


if __name__ == '__main__':
    complete_bookings()