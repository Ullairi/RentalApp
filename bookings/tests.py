from datetime import timedelta
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Booking
from users.models import User
from listings.models import Listing, Address


class BookingModelTest(TestCase):
    """Booking model tests"""
    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@example.com",
            username="owner",
            password="pass123",
            role="owner"
        )
        self.tenant = User.objects.create_user(
            email="tenant@example.com",
            username="tenant",
            password="pass123",
            role="tenant"
        )
        self.address = Address.objects.create(
            country="Germany",
            city="Berlin",
            street="Test Street",
            postal_code="12345"
        )
        self.listing = Listing.objects.create(
            owner=self.owner,
            title="Berlin Apartment",
            description="Central location in Berlin",
            address=self.address,
            price_per_night=100.00,
            bedrooms=2,
            bathrooms=1,
            max_stayers=4,
            house_type="apartment"
        )

    def test_booking_creation(self):
        """Test booking creation"""
        check_in = timezone.now().date() + timedelta(days=10)
        check_out = timezone.now().date() + timedelta(days=12)
        booking = Booking.objects.create(
            listing=self.listing,
            tenant=self.tenant,
            check_in=check_in,
            check_out=check_out,
            stayers=2
        )
        # 2 nights * 100 = 200
        self.assertEqual(booking.total_price, 200.00)
        self.assertEqual(booking.book_status, "pending")


class BookingAPITest(APITestCase):
    """Tests for booking API endpoints"""
    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@example.com",
            username="owner",
            password="pass123",
            role="owner"
        )
        self.tenant = User.objects.create_user(
            email="tenant@example.com",
            username="tenant",
            password="pass123",
            role="tenant"
        )
        self.address = Address.objects.create(
            country="Germany",
            city="Berlin",
            street="Test Street",
            postal_code="12345"
        )
        self.listing = Listing.objects.create(
            owner=self.owner,
            title="Berlin Apartment",
            description="Central location in Berlin",
            address=self.address,
            price_per_night=100.00,
            bedrooms=2,
            bathrooms=1,
            max_stayers=4,
            house_type="apartment"
        )

    def test_create_booking_tenant(self):
        """Test tenant can create a booking"""
        self.client.force_authenticate(user=self.tenant)
        url = reverse("booking-list-create")
        check_in = (timezone.now().date() + timedelta(days=10)).isoformat()
        check_out = (timezone.now().date() + timedelta(days=12)).isoformat()
        data = {
            "listing_id": self.listing.id,
            "check_in": check_in,
            "check_out": check_out,
            "stayers": 2
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Booking.objects.count(), 1)

    def test_create_booking_owner_forbidden(self):
        """Test owner cannot create a booking"""
        self.client.force_authenticate(user=self.owner)
        url = reverse("booking-list-create")
        check_in = (timezone.now().date() + timedelta(days=10)).isoformat()
        check_out = (timezone.now().date() + timedelta(days=12)).isoformat()
        data = {
            "listing_id": self.listing.id,
            "check_in": check_in,
            "check_out": check_out,
            "stayers": 2
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_bookings_tenant(self):
        """Test tenant can list their bookings"""
        self.client.force_authenticate(user=self.tenant)
        check_in = timezone.now().date() + timedelta(days=10)
        check_out = timezone.now().date() + timedelta(days=12)
        Booking.objects.create(
            listing=self.listing,
            tenant=self.tenant,
            check_in=check_in,
            check_out=check_out,
            stayers=2
        )
        url = reverse("booking-list-create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class BookingActionTest(APITestCase):
    """Tests for booking actions (cancel/confirm/reject)"""
    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@example.com",
            username="owner",
            password="pass123",
            role="owner"
        )
        self.tenant = User.objects.create_user(
            email="tenant@example.com",
            username="tenant",
            password="pass123",
            role="tenant"
        )
        self.address = Address.objects.create(
            country="Germany",
            city="Berlin",
            street="Test Street",
            postal_code="12345"
        )
        self.listing = Listing.objects.create(
            owner=self.owner,
            title="Berlin Apartment",
            description="Central location in Berlin",
            address=self.address,
            price_per_night=100.00,
            bedrooms=2,
            bathrooms=1,
            max_stayers=4,
            house_type="apartment"
        )
        self.booking = Booking.objects.create(
            listing=self.listing,
            tenant=self.tenant,
            check_in=timezone.now().date() + timedelta(days=10),
            check_out=timezone.now().date() + timedelta(days=12),
            stayers=2
        )

    def test_confirm_booking_owner(self):
        """Test owner can confirm a booking"""
        self.client.force_authenticate(user=self.owner)
        url = reverse("booking-confirm", args=[self.booking.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.book_status, "confirmed")

    def test_reject_booking_owner(self):
        """Test owner can reject a booking"""
        self.client.force_authenticate(user=self.owner)
        url = reverse("booking-reject", args=[self.booking.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.book_status, "rejected")

    def test_cancel_booking_tenant(self):
        """Test tenant can cancel their booking"""
        self.client.force_authenticate(user=self.tenant)
        url = reverse("booking-cancel", args=[self.booking.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.book_status, "cancelled")

    def test_confirm_booking_tenant_forbidden(self):
        """Test tenant cannot confirm a booking"""
        self.client.force_authenticate(user=self.tenant)
        url = reverse("booking-confirm", args=[self.booking.id])
        response = self.client.post(url)
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_400_BAD_REQUEST])

    def test_cancel_booking_owner_forbidden(self):
        """Test owner cannot cancel a booking"""
        self.client.force_authenticate(user=self.owner)
        url = reverse("booking-cancel", args=[self.booking.id])
        response = self.client.post(url)
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_400_BAD_REQUEST])