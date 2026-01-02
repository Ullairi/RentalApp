from rest_framework import serializers
from .models import Address, Listing, Amenity, ListingImg


class AmenitySerializer(serializers.ModelSerializer):
    """Serializer for amenities"""
    class Meta:
        model = Amenity
        fields = ['id', 'name', 'category', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class AddressSerializer(serializers.ModelSerializer):
    """Serializer for listing address"""
    full_address = serializers.CharField(read_only=True)

    class Meta:
        model = Address
        fields = ['id', 'country', 'city', 'land', 'street', 'postal_code', 'full_address', 'created_at']
        read_only_fields = ['id', 'full_address', 'created_at']


class ListingImgSerializer(serializers.ModelSerializer):
    """Serializer for listings images"""
    class Meta:
        model = ListingImg
        fields = ['id', 'img', 'main', 'created_at']
        read_only_fields = ['id', 'created_at']


class ListingSerializer(serializers.ModelSerializer):
    """Serializer for listing views"""
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    city = serializers.CharField(source='address.city', read_only=True)
    avg_rating = serializers.FloatField(read_only=True)
    main_img = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = [
            'id', 'title', 'created_at', 'city', 'owner_name', 'house_type',
            'max_stayers', 'bedrooms', 'bathrooms', 'price_per_night',
            'views_count', 'avg_rating', 'main_img', 'is_active']

    def get_main_img(self, obj):
        main_img = obj.images.filter(main=True).first()
        if main_img:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(main_img.img.url)
        return None


class ListingDetailSerializer(serializers.ModelSerializer):
    """Serializer for viewing listing details"""
    owner = serializers.StringRelatedField(read_only=True)
    address = AddressSerializer(read_only=True)
    amenities = AmenitySerializer(many=True, read_only=True)
    images = ListingImgSerializer(many=True, read_only=True)
    avg_rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Listing
        fields = [
            'id', 'title', 'description', 'address', 'owner', 'house_type', 'price_per_night',
            'bedrooms', 'bathrooms', 'max_stayers', 'amenities', 'images',
            'is_active', 'views_count', 'avg_rating', 'created_at', 'updated_at']


class ListingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating listings"""
    address = AddressSerializer()
    amenity_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    title = serializers.CharField(max_length=255, min_length=5)
    description = serializers.CharField(max_length=5000, min_length=20)
    price_per_night = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=1, max_value=100000)
    bedrooms = serializers.IntegerField(min_value=1, max_value=50)
    bathrooms = serializers.IntegerField(min_value=1, max_value=50)
    max_stayers = serializers.IntegerField(min_value=1, max_value=100)

    class Meta:
        model = Listing
        fields = [
            'title', 'description', 'address', 'house_type', 'max_stayers', 'price_per_night', 'bedrooms',
            'bathrooms', 'amenity_ids', 'is_active'
        ]

    def create(self, validated_data):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError('Authentication required')

        address_data = validated_data.pop('address')
        amenity_ids = validated_data.pop('amenity_ids', [])

        address = Address.objects.create(**address_data)
        listing = Listing.objects.create(owner=request.user, address=address, **validated_data)

        if amenity_ids:
            listing.amenities.set(amenity_ids)

        return listing

    def update(self, instance, validated_data):
        address_data = validated_data.pop('address', None)
        amenity_ids = validated_data.pop('amenity_ids', None)

        if address_data:
            for field, value in address_data.items():
                setattr(instance.address, field, value)
            instance.address.save()

        if amenity_ids is not None:
            instance.amenities.set(amenity_ids)

        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()

        return instance