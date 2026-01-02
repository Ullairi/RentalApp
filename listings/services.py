import logging
from django.db.models import Q, F, Count
from .models import Listing, ListingImg, SearchHistory, ViewHistory

logger = logging.getLogger(__name__)


class ListingService:
    """Service for listing logic"""
    @staticmethod
    def increment_views(listing, user=None):
        """Increase listing views counter by 1"""
        Listing.objects.filter(pk=listing.pk).update(views_count=F('views_count') + 1)

        ViewHistory.objects.create(
            listing=listing,
            user=user if user and user.is_authenticated else None
        )
        logger.info(f'Incremented views for listing {listing.id}')

    @staticmethod
    def toggle_active_status(listing):
        """Activating/deactivating listing status"""
        listing.is_active = not listing.is_active
        listing.save(update_fields=['is_active'])
        status = 'activated' if listing.is_active else 'deactivated'
        logger.info(f'Listing {listing.id} {status}')
        return listing

    @staticmethod
    def search_listings(query_params, user=None):
        """For searching and filtering listings by query parameters"""
        queryset = Listing.objects.filter(is_active=True).select_related(
            'owner', 'address'
        ).prefetch_related('amenities', 'images')

        search = query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(address__city__icontains=search)
            )

            SearchHistory.objects.create(
                query=search,
                user=user if user and user.is_authenticated else None
            )
            logger.info(f'Search recorded: {search}')

        min_price = query_params.get('min_price')
        max_price = query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price_per_night__gte=min_price)
        if max_price:
            queryset = queryset.filter(price_per_night__lte=max_price)

        city = query_params.get('city')
        if city:
            queryset = queryset.filter(address__city__icontains=city)

        min_bedrooms = query_params.get('min_bedrooms')
        if min_bedrooms:
            queryset = queryset.filter(bedrooms__gte=min_bedrooms)

        house_type = query_params.get('house_type')
        if house_type:
            queryset = queryset.filter(house_type=house_type)

        guests = query_params.get('guests')
        if guests:
            queryset = queryset.filter(max_stayers__gte=guests)

        return queryset

    @staticmethod
    def add_image(listing, img, main=False):
        """Adding image to listing"""
        if main:
            ListingImg.objects.filter(listing=listing, main=True).update(main=False)

        img_obj = ListingImg.objects.create(listing=listing, img=img, main=main)
        logger.info(f'Added image to listing {listing.id}')
        return img_obj

    @staticmethod
    def get_popular_searches(limit=10):
        """Service for getting popular searches"""
        return SearchHistory.objects.values('query').annotate(
            count=Count('id')
        ).order_by('-count')[:limit]

    @staticmethod
    def get_user_search_history(user, limit=20):
        """Service for getting users search history"""
        return SearchHistory.objects.filter(user=user).order_by('-created_at')[:limit]

    @staticmethod
    def get_user_view_history(user, limit=20):
        """Service for getting users view history"""
        return ViewHistory.objects.filter(user=user).select_related('listing').order_by('-created_at')[:limit]

    @staticmethod
    def get_popular_listings(limit=10):
        """Service for getting popular listings"""
        return Listing.objects.filter(is_active=True).order_by('-views_count')[:limit]