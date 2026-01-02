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