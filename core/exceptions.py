from rest_framework.exceptions import APIException
from rest_framework import status


class ListingNotAvailableError(APIException):
    """Exception if listing is unavailable"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Listing is unavailable for booking'
    default_code = 'listing_not_available'


class BookingNotAvailableError(APIException):
    """Exception if there is a booking conflict"""
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Chosen dates are unavailable for booking'
    default_code = 'booking_not_available'


class AccessRightsError(APIException):
    """Exception if there is not enough access rights"""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Not enough access rights for this operation'
    default_code = 'invalid_access_rights'


class DateRangeError(APIException):
    """Exception if there is invalid date range"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid date range'
    default_code = 'invalid_date_range'


class ReviewError(APIException):
    """Exception if user already left a review"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'User already left a review'
    default_code = 'already_reviewed'