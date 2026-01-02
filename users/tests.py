from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import User


class UserModelTest(TestCase):
    """Tests for the custom User model"""

    def test_user_creation(self):
        """Test regular user creation"""
        user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="securepassword123"
        )
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("securepassword123"))
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_active)

    def test_superuser_creation(self):
        """Test superuser creation"""
        superuser = User.objects.create_superuser(
            email="admin@example.com",
            username="admin",
            password="securepassword123"
        )
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertEqual(superuser.role, 'admin')


class RegisterViewTest(APITestCase):
    """Tests for user registration endpoint"""

    def test_register_tenant(self):
        """Test tenant registration"""
        url = reverse("register")
        data = {
            "email": "tenant@example.com",
            "username": "tenant1",
            "password": "SecurePass123!",
            "password_confirmation": "SecurePass123!",
            "role": "tenant"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="tenant@example.com").exists())
        user = User.objects.get(email="tenant@example.com")
        self.assertEqual(user.role, "tenant")

    def test_register_owner(self):
        """Test owner registration"""
        url = reverse("register")
        data = {
            "email": "owner@example.com",
            "username": "owner1",
            "password": "SecurePass123!",
            "password_confirmation": "SecurePass123!",
            "role": "owner"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email="owner@example.com")
        self.assertEqual(user.role, "owner")

    def test_register_admin_forbidden(self):
        """Test cannot register as admin"""
        url = reverse("register")
        data = {
            "email": "hacker@example.com",
            "username": "hacker",
            "password": "SecurePass123!",
            "password_confirmation": "SecurePass123!",
            "role": "admin"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_mismatch(self):
        """Test registration fails when passwords do not match"""
        url = reverse("register")
        data = {
            "email": "user@example.com",
            "username": "user1",
            "password": "ValidPass123!",
            "password_confirmation": "Mismatch123!",
            "role": "tenant"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_email(self):
        """Test registration fails with duplicate email"""
        User.objects.create_user(email="user@example.com", username="user1", password="pass123")
        url = reverse("register")
        data = {
            "email": "user@example.com",
            "username": "user2",
            "password": "pass123!!",
            "password_confirmation": "pass123!!",
            "role": "tenant"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CurrentUserViewTest(APITestCase):
    """Tests for current user detail endpoint"""
    def setUp(self):
        self.user = User.objects.create_user(
            email="current@example.com",
            username="currentuser",
            password="pass123"
        )

    def test_get_current_user(self):
        """Test authenticated user can retrieve their own data"""
        self.client.force_authenticate(user=self.user)
        url = reverse("user-me")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "current@example.com")

    def test_unauthenticated_access(self):
        """Test unauthenticated access is denied"""
        url = reverse("user-me")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PermissionTests(APITestCase):
    """Tests for role-based permissions"""
    def setUp(self):
        self.tenant = User.objects.create_user(
            email='tenant@example.com', password='TestPass123!',
            username='tenant', role='tenant'
        )
        self.owner = User.objects.create_user(
            email='owner@example.com', password='TestPass123!',
            username='owner', role='owner'
        )

    def test_tenant_cannot_create_listing(self):
        """Tenant cannot create listing"""
        self.client.force_authenticate(user=self.tenant)
        response = self.client.post('/api/listings/create/', {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)