from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_positive_price(value):
    """Validation that price is positive"""
    if value <= 0:
        raise ValidationError('Price cant be lower than 0', code='negative_price')


def validate_future_date(value):
    """Validation that date in a future"""
    if value < timezone.now().date():
        raise ValidationError('Date cant be in past', code='past_date')


def validate_positive_number(value):
    """Validation that number is positive"""
    if value <= 0:
        raise ValidationError('Number cant be equal or lower than 0', code='negative_number')


def validate_rating(value):
    """Validation that rating in range 1-5"""
    if value < 1 or value > 5:
        raise ValidationError('Rating must be in range between 1-5', code='invalid_rating')

def validate_no_digits(value):
    """Validation that value contains no digits"""
    if any(char.isdigit() for char in value):
        raise ValidationError('This field cannot contain numbers', code='contains_digits')

def validate_postal_code(value):
    """Validation that postal code is exactly 5 digits"""
    if not (value.isdigit() and len(value) == 5):
        raise ValidationError('Postal code must be exactly 5 digits', code='invalid_postal_code')

def validate_apartment_number(value):
    """Validation that apartment number contains only digits"""
    if value and not value.isdigit():
        raise ValidationError('Apartment number must contain only digits', code='invalid_apartment_number')
