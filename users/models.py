from django.db import models
from django.utils import timezone
from django.contrib.auth.models import PermissionsMixin, AbstractBaseUser, BaseUserManager
from phonenumber_field.modelfields import PhoneNumberField

from core.enums import Gender, UserRole
from core.mixins import TimestampMixin


class UserManager(BaseUserManager):
    """User manager"""
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password) # password hashing
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.update({
            'is_staff': True,
            'is_superuser': True,
            'role': UserRole.admin.name
        })
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, TimestampMixin):
    """User model"""
    username = models.CharField('Username', max_length=30, unique=True, blank=True)
    email = models.EmailField('Email', unique=True)
    first_name = models.CharField('First name', max_length=40, blank=True)
    last_name = models.CharField('Last name', max_length=40, blank=True)

    role = models.CharField(
        'Role', max_length=10,
        choices=UserRole.choices(),
        default=UserRole.tenant.name
    )
    gender = models.CharField(
        'Gender', max_length=10,
        choices=Gender.choices(),
        null=True, blank=True
    )
    birth_date = models.DateField('Birth date', null=True, blank=True)
    phone = PhoneNumberField('Phone number', null=True, blank=True)

    is_staff = models.BooleanField('Staff member', default=False)
    is_active = models.BooleanField('Active member', default=True)

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name} ({self.email})"
        return self.email

    def get_full_name(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.username

    def get_short_name(self):
        return self.first_name or self.username

    @property
    def age(self):
        if not self.birth_date:
            return None
        today = timezone.now().date()
        return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )

    @property
    def is_owner(self):
        return self.role == UserRole.owner.name

    @property
    def is_tenant(self):
        return self.role == UserRole.tenant.name

    @property
    def is_admin(self):
        return self.role == UserRole.admin.name

class Favorite(TimestampMixin):
    """Wish list model"""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='favorites', verbose_name='User'
    )
    listing = models.ForeignKey(
        'listings.Listing', on_delete=models.CASCADE,
        related_name='favorited_by', verbose_name='Listing'
    )

    class Meta:
        db_table = 'favorites'
        verbose_name = 'Favourite'
        verbose_name_plural = 'Favourites'
        unique_together = ('user', 'listing')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} -> {self.listing_id}"
