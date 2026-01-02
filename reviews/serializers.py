from rest_framework import serializers
from .models import Review, ReviewImg
from users.serializers import UserProfileSerializer


class ReviewImgSerializer(serializers.ModelSerializer):
    """Serializer for review images"""
    class Meta:
        model = ReviewImg
        fields = ['id', 'img', 'created_at']
        read_only_fields = ['id', 'created_at']

class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for viewing reviews list"""
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'author_name', 'rating', 'comment', 'created_at']

class ReviewDetailSerializer(serializers.ModelSerializer):
    """Serializer for viewing reviews details """
    author = UserProfileSerializer(read_only=True)
    listing_title = serializers.CharField(source='listing.title', read_only=True)
    images = ReviewImgSerializer(many=True, read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'author', 'listing_title', 'rating', 'comment', 'images', 'created_at', 'updated_at']

class ReviewCreateSerializer(serializers.ModelSerializer):
    """Serializer for review creation with validation"""
    listing_id = serializers.IntegerField(write_only=True)
    rating = serializers.IntegerField(min_value=1, max_value=5)
    comment = serializers.CharField(min_length=10, max_length=2000)

    class Meta:
        model = Review
        fields = ['listing_id', 'rating', 'comment']

    def create(self, validated_data):
        from listings.models import Listing
        from bookings.models import Booking
        from core.enums import BookingStatus

        listing_id = validated_data.pop('listing_id')
        user = self.context['request'].user

        try:
            listing = Listing.objects.get(id=listing_id, is_active=True)
        except Listing.DoesNotExist:
            raise serializers.ValidationError('Listing not found or inactive')

        if listing.owner == user:
            raise serializers.ValidationError('Cannot review your own listing')

        if Review.objects.filter(author=user, listing=listing).exists():
            raise serializers.ValidationError('You have already reviewed this listing')

        completed_booking = Booking.objects.filter(
            tenant=user,
            listing=listing,
            book_status=BookingStatus.completed.name
        ).first()

        if not completed_booking:
            raise serializers.ValidationError('You must have a completed booking to leave a review')

        review = Review.objects.create(
            author=user,
            listing=listing,
            booking=completed_booking,
            **validated_data
        )

        return review