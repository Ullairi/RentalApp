import logging
from django.db import transaction
from django.db.models import Q
from .models import Booking, BookingStatusHistory
from listings.models import Listing
from core.enums import BookingStatus
from core.exceptions import BookingNotAvailableError, ListingNotAvailableError, AccessRightsError

logger = logging.getLogger(__name__)


class BookingService:
    """Service for booking logic"""
    @staticmethod
    def calculate_price(listing, check_in, check_out):
        """Calculates booking price based on amount of nights"""
        nights = (check_out - check_in).days
        return listing.price_per_night * nights

    @staticmethod
    def check_availability(listing, check_in, check_out):
        """Checks if listing is available for chosen date"""
        overlapping = Booking.objects.filter(
            listing=listing,
            book_status='confirmed',
            check_in__lt=check_out,
            check_out__gt=check_in
        ).exists()
        return not overlapping

    @staticmethod
    def create_booking(tenant, validated_data):
        listing_id = validated_data.pop('listing_id')

        try:
            listing = Listing.objects.get(id=listing_id, is_active=True)
        except Listing.DoesNotExist:
            raise ListingNotAvailableError()

        if listing.owner == tenant:
            raise AccessRightsError('Cannot book your own listing')

        check_in = validated_data['check_in']
        check_out = validated_data['check_out']
        stayers = validated_data['stayers']

        if stayers > listing.max_stayers:
            raise ValueError(f'Maximum {listing.max_stayers} stayers allowed')

        if not BookingService.check_availability(listing, check_in, check_out):
            raise BookingNotAvailableError()

        total_price = BookingService.calculate_price(listing, check_in, check_out)

        with transaction.atomic():
            booking = Booking.objects.create(
                tenant=tenant,
                listing=listing,
                total_price=total_price,
                **validated_data
            )

            BookingStatusHistory.objects.create(
                booking=booking,
                history_status=BookingStatus.pending.name,
                comment='Booking created',
                changed_by=tenant
            )

            logger.info(f'Created booking {booking.id}')
            return booking

    @staticmethod
    def update_status(booking, new_status, user, comment=''):
        """Updating booking status"""
        with transaction.atomic():
            booking.book_status = new_status
            booking.save()

            BookingStatusHistory.objects.create(
                booking=booking,
                history_status=new_status,
                comment=comment,
                changed_by=user
            )

            logger.info(f'Booking {booking.id} -> {new_status}')
            return booking

    @staticmethod
    def confirm_booking(booking, user):
        if booking.listing.owner != user and not user.is_admin:
            raise AccessRightsError('Only owner can confirm')

        return BookingService.update_status(
            booking, BookingStatus.confirmed.name, user, 'Confirmed by owner'
        )

    @staticmethod
    def reject_booking(booking, user, reason=''):
        if booking.listing.owner != user and not user.is_admin:
            raise AccessRightsError('Only can be rejected by an owner')

        return BookingService.update_status(
            booking, BookingStatus.rejected.name, user, reason or 'Rejected'
        )

    @staticmethod
    def cancel_booking(booking, user):
        if booking.tenant != user and not user.is_admin:
            raise AccessRightsError('Only can be canceled by tenant')

        if not booking.cancelation:
            raise ValueError('Not possible to cancel this booking')

        return BookingService.update_status(
            booking, BookingStatus.cancelled.name, user, 'Cancelled by tenant'
        )