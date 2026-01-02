import logging
from django.db import transaction
from .models import User, Favorite
from listings.models import Listing
from core.exceptions import AccessRightsError

logger = logging.getLogger(__name__)


class UserService:
    """Service for working with user logic"""
    @staticmethod
    def create_user(validated_data):
        with transaction.atomic():
            user = User.objects.create_user(**validated_data)
            logger.info(f'Created new user: {user.email}')
            return user

    @staticmethod
    def update_user_profile(user, validated_data):
        for field, val in validated_data.items():
            setattr(user, field, val)
        user.save()
        logger.info(f'User profile updated: {user.email}')
        return user

    @staticmethod
    def user_statistic(user):
        stats = {
            'favorites_count': user.favorites.count(),
            'listings_count': 0,
            'bookings_count': 0,
            'reviews_count': 0,
        }
        if user.is_owner and hasattr(user, 'listings'):
            stats['listings_count'] = user.listings.count()
        if user.is_tenant:
            if hasattr(user, 'bookings'):
                stats['bookings_count'] = user.bookings.count()
            if hasattr(user, 'reviews'):
                stats['reviews_count'] = user.reviews.count()
        return stats

class FavoriteService:
    """Service for managing wish list"""
    @staticmethod
    def add_to_favorites(user, listing_id):
        try:
            listing = Listing.objects.get(id=listing_id, is_active=True)
        except Listing.DoesNotExist:
            raise ValueError('Listing not found or unavailable')

        if listing.owner == user:
            raise AccessRightsError('Cannot add own listing to favorites')

        favorite, created = Favorite.objects.get_or_create(user=user, listing=listing)
        if not created:
            raise ValueError('Already in favorites')

        logger.info(f'User {user.email} added to favorites: {listing_id}')
        return favorite

    @staticmethod
    def remove_from_favorites(user, listing_id):
        deleted, _ = Favorite.objects.filter(user=user, listing_id=listing_id).delete()
        return deleted > 0