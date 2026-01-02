import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListAPIView, RetrieveAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Booking
from .serializers import BookingSerializer, BookingDetailSerializer, BookingCreateSerializer
from .services import BookingService
from users.permissions import Tenant

logger = logging.getLogger(__name__)


class BookingListCreateView(ListCreateAPIView):
    """Lists and create user bookings"""
    permission_classes = [Tenant]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BookingCreateSerializer
        return BookingSerializer

    def get_queryset(self):
        return Booking.objects.filter(tenant=self.request.user).select_related('listing', 'tenant')

    def perform_create(self, serializer):
        booking = BookingService.create_booking(self.request.user, serializer.validated_data)
        serializer.instance = booking

class BookingDetailView(RetrieveAPIView):
    """Retrieves booking details"""
    serializer_class = BookingDetailSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Booking.objects.all()
        return Booking.objects.filter(tenant=user) | Booking.objects.filter(listing__owner=user)

class OwnerBookingsView(ListAPIView):
    """Bookings list received by owner"""
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(listing__owner=self.request.user).select_related('tenant', 'listing')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_booking(request, pk):
    """Booking confirmation"""
    try:
        booking = Booking.objects.get(pk=pk)
        booking = BookingService.confirm_booking(booking, request.user)
        return Response({'id': booking.id, 'book_status': booking.book_status, 'message': 'Booking confirmed'})
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_booking(request, pk):
    """Booking rejection"""
    try:
        booking = Booking.objects.get(pk=pk)
        reason = request.data.get('reason', '')
        booking = BookingService.reject_booking(booking, request.user, reason)
        return Response({'id': booking.id, 'book_status': booking.book_status, 'message': 'Booking rejected'})
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_booking(request, pk):
    """Booking cancellation"""
    try:
        booking = Booking.objects.get(pk=pk)
        booking = BookingService.cancel_booking(booking, request.user)
        return Response({'id': booking.id, 'book_status': booking.book_status, 'message': 'Booking cancelled'})
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)