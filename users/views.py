import logging
from datetime import datetime, timezone

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.generics import ListAPIView, RetrieveAPIView, ListCreateAPIView, RetrieveDestroyAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from django.contrib.auth import authenticate

from drf_spectacular.utils import extend_schema #for swagger

from .models import User, Favorite
from .serializers import (
    UserSerializer, LoginSerializer, UserProfileSerializer,
    UserInfoUpdateSerializer, FavoriteSerializer
)
from .services import UserService, FavoriteService
from .throttling import LoginRateThrottle, RegisterRateThrottle

logger = logging.getLogger(__name__)

def set_jwt_cookies(response, user):
    """Create JWT tokens and store them in cookies"""
    refresh = RefreshToken.for_user(user)
    access = refresh.access_token

    response.set_cookie(
        'access_token', str(access),
        httponly=True,
        secure=False,
        samesite='Lax', #basic CSRF protection(Cross-Site Request Forgery)
        expires=datetime.fromtimestamp(access['exp'], tz=timezone.utc)
    )
    response.set_cookie(
        'refresh_token', str(refresh),
        httponly=True,
        secure=False,
        samesite='Lax',
        expires=datetime.fromtimestamp(refresh['exp'], tz=timezone.utc)
    )
    return response

@extend_schema(
    request=UserSerializer,
    responses={201: UserProfileSerializer},
    description='Register a new user'
)
@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([RegisterRateThrottle])
def register(request):
    """Responsible for user reg."""
    serializer = UserSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    data.pop('password_confirmation')
    user = UserService.create_user(data)

    response = Response(
        {'message': 'Registration successful', 'user': UserProfileSerializer(user).data},
        status=status.HTTP_201_CREATED
    )
    return set_jwt_cookies(response, user)

@extend_schema(
    request=LoginSerializer,
    responses={200: UserProfileSerializer},
    description='Login with email and password'
)
@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([LoginRateThrottle])
def login(request):
    """User authenticate and JWT tokens issuing"""
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(
        request,
        username=serializer.validated_data['email'],
        password=serializer.validated_data['password']
    )

    if not user:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    if not user.is_active:
        return Response({'error': 'Account is inactive'}, status=status.HTTP_403_FORBIDDEN)

    response = Response(
        {'message': 'Login successful', 'user': UserProfileSerializer(user).data}
    )
    logger.info(f'User logged in: {user.email}')
    return set_jwt_cookies(response, user)

@extend_schema(
    request=None,
    responses={200: dict},
    description='Logout and clear cookies'
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """User logout"""
    response = Response({'message': 'Logged out successfully'})
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    return response

@extend_schema(
    request=None,
    responses={200: dict},
    description='Refresh JWT token from cookie'
)
@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    """JWT tokens refresh"""
    token = request.COOKIES.get('refresh_token')
    if not token:
        return Response({'error': 'Refresh token not found'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        refresh = RefreshToken(token)
        user = User.objects.get(id=refresh['user_id'])
        response = Response({'message': 'Token refreshed'})
        return set_jwt_cookies(response, user)
    except (TokenError, User.DoesNotExist):
        return Response({'error': 'Invalid refresh token'}, status=status.HTTP_401_UNAUTHORIZED)

class UserListView(ListAPIView):
    """List of active users"""
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'gender']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-created_at']

class UserDetailView(RetrieveAPIView):
    """View of a one user profile"""
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

@extend_schema(
    responses={200: UserProfileSerializer},
    description='Get current authenticated user profile'
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """Returns a current user"""
    return Response(UserProfileSerializer(request.user).data)


@extend_schema(
    request=UserInfoUpdateSerializer,
    responses={200: UserProfileSerializer},
    description='Update current user profile'
)
@api_view(['PATCH', 'PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """Responsible for updating user info in profile"""
    serializer = UserInfoUpdateSerializer(data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user = UserService.update_user_profile(request.user, serializer.validated_data)
    return Response(UserProfileSerializer(user).data)

@extend_schema(
    responses={200: dict},
    description='Get user statistics (favorites, bookings, reviews count)'
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_statistics(request):
    """Returns user statistic"""
    return Response(UserService.user_statistic(request.user))

class FavoriteListCreateView(ListCreateAPIView):
    """Lists and adding wishlisted listing"""
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering = ['-created_at']

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).select_related('listing')

    def create(self, request, *args, **kwargs):
        listing_id = request.data.get('listing_id')
        if not listing_id:
            return Response({'error': 'listing_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            favorite = FavoriteService.add_to_favorites(request.user, listing_id)
            return Response(FavoriteSerializer(favorite).data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class FavoriteDetailView(RetrieveDestroyAPIView):
    """Removal or retrieve of wishlisted i"""
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)