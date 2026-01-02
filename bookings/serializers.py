from rest_framework import serializers
from django.utils import timezone
from .models import Booking, BookingStatusHistory
from listings.serializers import ListingSerializer
from users.serializers import UserProfileSerializer


class BookingStatusHistorySerializer(serializers.ModelSerializer):
    """Serializer for booking status history"""
    changed_by = serializers.StringRelatedField()

    class Meta:
        model = BookingStatusHistory
        fields = ['id', 'history_status', 'comment', 'changed_by', 'created_at']

class BookingSerializer(serializers.ModelSerializer):
    """Serializer for viewing booking list"""
    listing_title = serializers.CharField(source='listing.title', read_only=True)
    tenant_name = serializers.CharField(source='tenant.get_full_name', read_only=True)
    nights_to_stay = serializers.IntegerField(read_only=True)
    cancelation = serializers.BooleanField(read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'tenant_name', 'listing_title', 'check_in', 'check_out',
            'stayers', 'total_price', 'book_status', 'nights_to_stay', 'cancelation', 'created_at'
        ]

class BookingDetailSerializer(serializers.ModelSerializer):
    """Serializer for viewing booking detail"""
    listing = ListingSerializer(read_only=True)
    tenant = UserProfileSerializer(read_only=True)
    status_history = BookingStatusHistorySerializer(many=True, read_only=True)
    nights_to_stay = serializers.IntegerField(read_only=True)
    cancelation = serializers.BooleanField(read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'tenant', 'listing', 'check_in', 'check_out', 'stayers',
            'total_price', 'book_status', 'nights_to_stay', 'cancelation',
            'status_history', 'created_at', 'updated_at'
        ]


class BookingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new booking"""
    listing_id = serializers.IntegerField(write_only=True)
    stayers = serializers.IntegerField(min_value=1, max_value=100)

    class Meta:
        model = Booking
        fields = ['listing_id', 'check_in', 'check_out', 'stayers']

    def validate(self, data):
        if data['check_out'] <= data['check_in']:
            raise serializers.ValidationError({'check_out': 'Check-out must be after check-in'})

        if data['check_in'] < timezone.now().date():
            raise serializers.ValidationError({'check_in': 'Check-in cannot be in the past'})

        nights = (data['check_out'] - data['check_in']).days
        if nights > 365:
            raise serializers.ValidationError({'check_out': 'Maximum booking length is 365 days'})

        from listings.models import Listing
        try:
            listing = Listing.objects.get(id=data['listing_id'], is_active=True)
            if data['stayers'] > listing.max_stayers:
                raise serializers.ValidationError({
                    'stayers': f'Maximum {listing.max_stayers} guests allowed'
                })
        except Listing.DoesNotExist:
            raise serializers.ValidationError({'listing_id': 'Listing not found or inactive'})

        return data

    def create(self, validated_data):
        from listings.models import Listing

        listing_id = validated_data.pop('listing_id')
        listing = Listing.objects.get(id=listing_id)

        nights_to_stay = (validated_data['check_out'] - validated_data['check_in']).days
        total_price = listing.price_per_night * nights_to_stay

        booking = Booking.objects.create(
            tenant=self.context['request'].user,
            listing=listing,
            total_price=total_price,
            **validated_data
        )

        BookingStatusHistory.objects.create(
            booking=booking,
            history_status=booking.book_status,
            changed_by=self.context['request'].user
        )

        return booking