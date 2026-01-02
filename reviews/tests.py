from datetime import timedelta
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Review
from users.models import User
from listings.models import Listing, Address
from bookings.models import Booking


class ReviewModelTest(TestCase):
    """Tests for the Review model"""
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
            bedrooms=3,
            bathrooms=1,
            max_stayers=4,
            house_type="apartment"
        )
        self.booking = Booking.objects.create(
            listing=self.listing,
            tenant=self.tenant,
            check_in=timezone.now().date() - timedelta(days=10),
            check_out=timezone.now().date() - timedelta(days=5),
            stayers=2,
            book_status="completed"
        )

    def test_review_creation(self):
        """Test creating a review"""
        review = Review.objects.create(
            listing=self.listing,
            author=self.tenant,
            booking=self.booking,
            rating=5,
            comment="Great place to stay!"
        )
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.listing, self.listing)
        self.assertEqual(review.author, self.tenant)

    def test_one_review_per_listing_per_user(self):
        """Test that only one review per listing per user is allowed"""
        Review.objects.create(
            listing=self.listing,
            author=self.tenant,
            booking=self.booking,
            rating=4,
            comment="Nice place"
        )
        with self.assertRaises(Exception):
            Review.objects.create(
                listing=self.listing,
                author=self.tenant,
                booking=self.booking,
                rating=5,
                comment="Another review"
            )


class ReviewAPITest(APITestCase):
    """Tests for review API endpoints"""
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
            bedrooms=3,
            bathrooms=1,
            max_stayers=4,
            house_type="apartment"
        )
        self.booking = Booking.objects.create(
            listing=self.listing,
            tenant=self.tenant,
            check_in=timezone.now().date() - timedelta(days=10),
            check_out=timezone.now().date() - timedelta(days=5),
            stayers=2,
            book_status="completed"
        )

    def test_create_review_tenant(self):
        """Test tenant can create a review after completed stay"""
        self.client.force_authenticate(user=self.tenant)
        url = reverse("review-create")
        data = {
            "listing_id": self.listing.id,
            "rating": 5,
            "comment": "Excellent place to stay!"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Review.objects.filter(author=self.tenant, listing=self.listing).exists())

    def test_create_review_without_completed_booking(self):
        """Test review creation is blocked without completed booking"""
        other_tenant = User.objects.create_user(
            email="other@example.com",
            username="other",
            password="pass123",
            role="tenant"
        )
        self.client.force_authenticate(user=other_tenant)
        url = reverse("review-create")
        data = {
            "listing_id": self.listing.id,
            "rating": 5,
            "comment": "Not allowed without booking!"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_review_owner_forbidden(self):
        """Test owner cannot review their own listing"""
        self.client.force_authenticate(user=self.owner)
        url = reverse("review-create")
        data = {
            "listing_id": self.listing.id,
            "rating": 5,
            "comment": "Can't review my own listing!"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_reviews_public(self):
        """Test public access to listing reviews"""
        Review.objects.create(
            listing=self.listing,
            author=self.tenant,
            booking=self.booking,
            rating=5,
            comment="Great!"
        )
        url = reverse("listing-reviews", kwargs={"listing_id": self.listing.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_review_unauthenticated(self):
        """Test unauthenticated users cannot create reviews"""
        url = reverse("review-create")
        data = {
            "listing_id": self.listing.id,
            "rating": 5,
            "comment": "Anonymous review"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_duplicate_review_forbidden(self):
        """Test user cannot review same listing twice"""
        Review.objects.create(
            listing=self.listing,
            author=self.tenant,
            booking=self.booking,
            rating=4,
            comment="First review"
        )
        self.client.force_authenticate(user=self.tenant)
        url = reverse("review-create")
        data = {
            "listing_id": self.listing.id,
            "rating": 5,
            "comment": "Second review attempt"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)