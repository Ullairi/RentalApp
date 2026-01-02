from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Favorite


class UserSerializer(serializers.ModelSerializer):
    """User serializer for registration"""
    password = serializers.CharField(
        write_only=True, required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirmation = serializers.CharField(
        write_only=True, required=True,
        style={'input_type': 'password'}
    )
    role = serializers.ChoiceField(
        choices=[('tenant', 'Tenant'), ('owner', 'Owner')],
        default='tenant'
    )

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'password', 'password_confirmation',
            'first_name', 'last_name', 'role', 'gender', 'birth_date', 'phone'
        ]

    def validate_role(self, value):
        """Prevent registration as admin"""
        if value == 'admin':
            raise serializers.ValidationError('Cannot register as admin')
        return value

    def validate(self, data): #password validation
        if data.get('password') != data.get('password_confirmation'):
            raise serializers.ValidationError({
                'password_confirmation': 'Passwords do not match'
            })
        return data


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True, required=True,
        style={'input_type': 'password'}
    )


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    age = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'role', 'gender', 'birth_date', 'age',
            'phone', 'is_owner', 'is_tenant', 'created_at'
        ]
        read_only_fields = fields


class UserInfoUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user info"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'gender', 'birth_date', 'phone']


class FavoriteSerializer(serializers.ModelSerializer):
    """Serializer for user wish list"""
    user = UserProfileSerializer(read_only=True)
    listing_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'user', 'listing', 'listing_id', 'created_at']
        read_only_fields = ['id', 'user', 'listing', 'created_at']