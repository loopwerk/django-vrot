from typing import Callable
from urllib.parse import unquote
from zoneinfo import ZoneInfo

from django.http import HttpRequest, HttpResponse
from django.utils import timezone


class TimezoneMiddleware:
    """
    Middleware that activates a timezone based on a user's cookie.

    This middleware reads a 'timezone' cookie set by the included JavaScript
    and activates that timezone for the duration of the request. This allows
    Django to render all times in the user's local timezone.

    The timezone cookie should contain a valid timezone name (e.g., 'America/New_York').
    If the timezone is invalid or missing, the middleware falls back to Django's
    default timezone behavior.

    Usage:
        Add to MIDDLEWARE in settings.py:

        MIDDLEWARE = [
            ...
            'vrot.middleware.TimezoneMiddleware',
        ]
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        tzname = request.COOKIES.get("timezone")
        if tzname:
            try:
                # Decode URL-encoded timezone name (e.g., "Europe%2FAmsterdam" -> "Europe/Amsterdam")
                tzname = unquote(tzname)
                timezone.activate(ZoneInfo(tzname))
            except Exception:
                timezone.deactivate()  # fallback to UTC
        else:
            timezone.deactivate()

        return self.get_response(request)
