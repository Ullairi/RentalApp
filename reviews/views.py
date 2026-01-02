import logging
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import Review
from .serializers import ReviewSerializer, ReviewCreateSerializer
from .services import ReviewService
from core.exceptions import ReviewError
from users.permissions import AdminOrOwner


logger = logging.getLogger(__name__)

class ListingReviewsView(ListAPIView):
    """Lists all reviews of a specific listing"""
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        listing_id = self.kwargs.get('listing_id')
        return Review.objects.filter(listing_id=listing_id).select_related('author')

class MyReviewsView(ListAPIView):
    """Lists all reviews created by current user"""
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Review.objects.filter(author=self.request.user).select_related('listing')

class ReviewCreateView(CreateAPIView):
    """New review creation"""
    serializer_class = ReviewCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            review = ReviewService.create_review(request.user, serializer.validated_data)
            return Response(
                ReviewSerializer(review, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        except ReviewError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ReviewManageView(RetrieveUpdateDestroyAPIView):
    """Delete, create or retrieve review"""
    serializer_class = ReviewSerializer
    permission_classes = [AdminOrOwner]
    lookup_field = 'pk'

    def get_queryset(self):
        if self.request.user.is_admin:
            return Review.objects.all()
        return Review.objects.filter(author=self.request.user)