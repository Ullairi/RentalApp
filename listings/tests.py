from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Listing, Address, SearchHistory, ViewHistory
from users.models import User


class ListingModelTest(TestCase):
    """Tests for the Listing model"""
    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@example.com",
            username="owner",
            password="pass123",
            role="owner"
        )
        self.address = Address.objects.create(
            country="Germany",
            city="Berlin",
            street="Test Street",
            postal_code="12345"
        )

    def test_listing_creation(self):
        """Test listing creation with default active state"""
        listing = Listing.objects.create(
            owner=self.owner,
            title="Cozy Apartment",
            description="Nice place in Berlin",
            address=self.address,
            price_per_night=100.00,
            bedrooms=2,
            bathrooms=1,
            max_stayers=4,
            house_type="apartment"
        )
        self.assertEqual(listing.title, "Cozy Apartment")
        self.assertTrue(listing.is_active)


class ListingListViewTest(APITestCase):
    """Tests for listings list view and creation"""
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

    def test_list_listings_public(self):
        """Test public access to listing list"""
        url = reverse("listing-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_listing_owner(self):
        """Test owner can create a listing"""
        self.client.force_authenticate(user=self.owner)
        url = reverse("listing-create")
        data = {
            "title": "New Listing Here",
            "description": "Great place to stay in Munich",
            "address": {
                "country": "Germany",
                "city": "Munich",
                "street": "Main Street",
                "postal_code": "80331"
            },
            "price_per_night": "150.00",
            "bedrooms": 2,
            "bathrooms": 1,
            "max_stayers": 4,
            "house_type": "apartment"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_listing_tenant_forbidden(self):
        """Test tenant cannot create a listing"""
        self.client.force_authenticate(user=self.tenant)
        url = reverse("listing-create")
        data = {
            "title": "New Listing",
            "description": "Great place to stay",
            "address": {
                "country": "Germany",
                "city": "Munich",
                "street": "Main Street",
                "postal_code": "80331"
            },
            "price_per_night": "150.00",
            "bedrooms": 2,
            "bathrooms": 1,
            "max_stayers": 4,
            "house_type": "apartment"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ListingDetailViewTest(APITestCase):
    """Tests for listing detail view"""
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

    def test_retrieve_listing_public(self):
        """Test public access to listing detail"""
        url = reverse("listing-detail", args=[self.listing.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Berlin Apartment")

    def test_update_listing_owner(self):
        """Test owner can update their listing"""
        self.client.force_authenticate(user=self.owner)
        url = reverse("listing-manage", args=[self.listing.id])
        data = {"title": "Updated Title", "description": "Updated description here"}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_listing_non_owner_forbidden(self):
        """Test non-owner cannot update listing"""
        self.client.force_authenticate(user=self.tenant)
        url = reverse("listing-manage", args=[self.listing.id])
        data = {"title": "Hacked Title"}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)  # queryset filtered

    def test_delete_listing_owner(self):
        """Test owner can delete their listing"""
        self.client.force_authenticate(user=self.owner)
        url = reverse("listing-manage", args=[self.listing.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class ListingHistoryTest(APITestCase):
    """Tests for search and view history"""
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

    def test_view_saves_history(self):
        """Test that listing views are saved to history"""
        self.client.force_authenticate(user=self.tenant)
        url = reverse("listing-detail", args=[self.listing.id])
        self.client.get(url)
        self.assertTrue(ViewHistory.objects.filter(listing=self.listing, user=self.tenant).exists())

    def test_search_saves_history(self):
        """Test that search queries are saved to history"""
        self.client.force_authenticate(user=self.tenant)
        url = reverse("listing-list")
        self.client.get(url, {"search": "Berlin"})
        self.assertTrue(SearchHistory.objects.filter(query="Berlin", user=self.tenant).exists())

    def test_popular_listings(self):
        """Test retrieving popular listings"""
        url = reverse("popular-listings")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)