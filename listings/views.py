from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import (
    ListAPIView, RetrieveAPIView,
    ListCreateAPIView, RetrieveUpdateDestroyAPIView
)
from rest_framework import filters
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema

from .models import Listing, Amenity
from .serializers import (
    ListingSerializer, ListingDetailSerializer,
    ListingCreateSerializer, AmenitySerializer,
    ListingImgSerializer
)
from .services import ListingService
from users.permissions import Owner, AdminOrOwner


class ListingListView(ListAPIView):
    """List of active listings with search and filtering options"""
    serializer_class = ListingSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ['price_per_night', 'created_at', 'views_count']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user if self.request.user.is_authenticated else None
        return ListingService.search_listings(self.request.query_params, user)

class ListingDetailView(RetrieveAPIView):
    """Listing detail view"""
    queryset = Listing.objects.filter(is_active=True).select_related(
        'owner', 'address'
    ).prefetch_related('amenities', 'images')
    serializer_class = ListingDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'pk'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user if request.user.is_authenticated else None
        ListingService.increment_views(instance, user)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class ListingCreateView(ListCreateAPIView):
    """Creating and listing of listings by user"""
    serializer_class = ListingCreateSerializer
    permission_classes = [Owner]

    def get_queryset(self):
        return Listing.objects.filter(owner=self.request.user)

class ListingManageView(RetrieveUpdateDestroyAPIView):
    """deletion, update or retrieval of listing"""
    serializer_class = ListingCreateSerializer
    permission_classes = [AdminOrOwner]
    lookup_field = 'pk'

    def get_queryset(self):
        if self.request.user.is_admin:
            return Listing.objects.all()
        return Listing.objects.filter(owner=self.request.user)

@api_view(['POST'])
@permission_classes([AdminOrOwner])
def toggle_listing_status(request, pk):
    """Activation/deactivation of listing"""
    try:
        if request.user.is_admin:
            listing = Listing.objects.get(pk=pk)
        else:
            listing = Listing.objects.get(pk=pk, owner=request.user)
    except Listing.DoesNotExist:
        return Response({'error': 'Listing not found'}, status=status.HTTP_404_NOT_FOUND)

    listing = ListingService.toggle_active_status(listing)
    return Response({
        'id': listing.id,
        'is_active': listing.is_active,
        'message': f'Listing {"activated" if listing.is_active else "deactivated"}'
    })

class AmenityListView(ListAPIView):
    """List of amenities"""
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer
    permission_classes = [AllowAny]

@api_view(['POST'])
@permission_classes([Owner])
def add_listing_image(request, pk):
    """Adding image to listing"""
    try:
        listing = Listing.objects.get(pk=pk, owner=request.user)
    except Listing.DoesNotExist:
        return Response({'error': 'Listing not found'}, status=status.HTTP_404_NOT_FOUND)

    img = request.FILES.get('image')
    if not img:
        return Response({'error': 'Image file is required'}, status=status.HTTP_400_BAD_REQUEST)

    main = request.data.get('main', 'false').lower() == 'true'
    img_obj = ListingService.add_image(listing, img, main)

    serializer = ListingImgSerializer(img_obj, context={'request': request})
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@extend_schema(responses={200: dict}, description='Get popular search queries')
@api_view(['GET'])
@permission_classes([AllowAny])
def popular_searches(request):
    """List of popular search queries"""
    searches = ListingService.get_popular_searches(limit=10)
    return Response(list(searches))

@extend_schema(responses={200: dict}, description='Get current user search history')
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_search_history(request):
    """User search history"""
    history = ListingService.get_user_search_history(request.user, limit=20)
    return Response([
        {'query': h.query, 'created_at': h.created_at}
        for h in history
    ])

@extend_schema(responses={200: dict}, description='Get current user view history')
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_view_history(request):
    """User view history"""
    history = ListingService.get_user_view_history(request.user, limit=20)
    return Response([
        {
            'listing_id': h.listing.id,
            'listing_title': h.listing.title,
            'created_at': h.created_at
        }
        for h in history
    ])

@extend_schema(responses={200: ListingSerializer(many=True)}, description='Get most popular listings')
@api_view(['GET'])
@permission_classes([AllowAny])
def popular_listings(request):
    """List of most popular listings by views"""
    listings = ListingService.get_popular_listings(limit=10)
    serializer = ListingSerializer(listings, many=True, context={'request': request})
    return Response(serializer.data)