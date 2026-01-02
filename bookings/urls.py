from django.urls import path
from . import views

urlpatterns = [
    path('bookings/', views.BookingListCreateView.as_view(), name='booking-list-create'),

    path('bookings/received/', views.OwnerBookingsView.as_view(), name='owner-bookings'),
    path('bookings/<int:pk>/', views.BookingDetailView.as_view(), name='booking-detail'),
    path('bookings/<int:pk>/confirm/', views.confirm_booking, name='booking-confirm'),
    path('bookings/<int:pk>/reject/', views.reject_booking, name='booking-reject'),
    path('bookings/<int:pk>/cancel/', views.cancel_booking, name='booking-cancel'),
]