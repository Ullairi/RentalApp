import logging
from django.db import transaction, IntegrityError
from .models import Review
from listings.models import Listing
from bookings.models import Booking
from core.enums import BookingStatus
from core.exceptions import ReviewError


logger = logging.getLogger(__name__)

class ReviewService:
    """Service for reviews logic"""
    @staticmethod
    def can_review(user, listing):
        if listing.owner == user:
            raise ReviewError('Cannot review your own listing')

        if Review.objects.filter(listing=listing, author=user).exists():
            raise ReviewError('You have already reviewed this listing')

        completed_booking = Booking.objects.filter(
            listing=listing,
            tenant=user,
            book_status=BookingStatus.completed.name).first()

        if not completed_booking:
            raise ReviewError('You must have a completed booking to leave a review')

        return completed_booking

    @staticmethod
    def create_review(author, validated_data):
        listing_id = validated_data.pop('listing_id')

        try:
            listing = Listing.objects.get(id=listing_id, is_active=True)
        except Listing.DoesNotExist:
            raise ReviewError('Listing not found or inactive')

        booking = ReviewService.can_review(author, listing)

        with transaction.atomic():
            try:
                review = Review.objects.create(
                    listing=listing,
                    author=author,
                    booking=booking,
                    **validated_data
                )
            except IntegrityError:
                raise ReviewError('You have already reviewed this listing')

        logger.info(f'Created review {review.id} for listing {listing.id}')
        return review