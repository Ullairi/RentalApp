from rest_framework.throttling import AnonRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    """
    Rate limit for login attempts
    Prevents auth endpoints from force-spam attacks
    """
    scope = 'login'


class RegisterRateThrottle(AnonRateThrottle):
    """
    Rate limit for user registration
    Prevents accounts creation spam
    """
    scope = 'register'