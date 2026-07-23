"""Lightweight token authentication for MongoEngine-backed users.

Uses Django's signed, timestamped tokens (``django.core.signing``) so we don't
need a separate token table or an extra dependency such as PyJWT. Tokens are
stateless and expire after ``TOKEN_MAX_AGE_SECONDS``.
"""

from django.core import signing
from rest_framework import authentication, exceptions

from utils.mongo_documents import UserProfile

TOKEN_SALT = "hiresense.auth.token"
TOKEN_MAX_AGE_SECONDS = 60 * 60 * 24 * 7  # 7 days


def create_token(user):
    """Return a signed token identifying the given UserProfile."""
    return signing.dumps(
        {"uid": str(user.id), "email": user.email},
        salt=TOKEN_SALT,
    )


class AuthUser:
    """Minimal ``request.user`` stand-in for a MongoEngine UserProfile.

    DRF's permission checks only need ``is_authenticated``; the extra
    attributes let views tie a session to the real, verified user instead of
    trusting a client-supplied email.
    """

    is_authenticated = True
    is_anonymous = False

    def __init__(self, profile):
        self.profile = profile
        self.id = str(profile.id)
        self.email = profile.email
        self.full_name = profile.full_name or ""

    def __str__(self):
        return self.email


def get_user_from_token(token):
    try:
        data = signing.loads(token, salt=TOKEN_SALT, max_age=TOKEN_MAX_AGE_SECONDS)
    except signing.SignatureExpired:
        raise exceptions.AuthenticationFailed("Token has expired. Please log in again.")
    except signing.BadSignature:
        raise exceptions.AuthenticationFailed("Invalid authentication token.")

    profile = UserProfile.objects(email=data.get("email")).first()
    if not profile:
        raise exceptions.AuthenticationFailed("User no longer exists.")
    return AuthUser(profile)


class MongoTokenAuthentication(authentication.BaseAuthentication):
    """Reads ``Authorization: Bearer <token>`` and resolves the user."""

    keyword = "Bearer"

    def authenticate(self, request):
        header = authentication.get_authorization_header(request).decode("utf-8")
        if not header:
            return None  # No credentials supplied; permissions decide the outcome.

        parts = header.split()
        if parts[0].lower() != self.keyword.lower():
            return None  # A different auth scheme; not ours to handle.
        if len(parts) != 2:
            raise exceptions.AuthenticationFailed("Invalid Authorization header format.")

        user = get_user_from_token(parts[1])
        return (user, parts[1])

    def authenticate_header(self, request):
        return self.keyword
