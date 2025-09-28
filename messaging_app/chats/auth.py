"""Helpers related to authentication configuration.

This module is intentionally small — authentication is configured via
REST_FRAMEWORK and SimpleJWT settings in settings.py. We provide this file
as a place for any auth-related helpers in the future.
"""

from rest_framework_simplejwt.tokens import RefreshToken


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
