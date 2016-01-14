from unittest.mock import Mock
from zoneinfo import ZoneInfo

import pytest
from django.test import RequestFactory
from django.utils import timezone

from vrot.middleware import TimezoneMiddleware


@pytest.fixture
def middleware():
    def get_response(request):
        return Mock()

    return TimezoneMiddleware(get_response)


@pytest.fixture
def request_factory():
    return RequestFactory()


class TestTimezoneMiddleware:
    def teardown_method(self):
        """Clean up timezone state after each test"""
        timezone.deactivate()

    def test_no_timezone_cookie(self, middleware, request_factory):
        """Without timezone cookie, should use default timezone"""
        request = request_factory.get("/")
        request.COOKIES = {}

        # Set a known timezone first
        timezone.activate(ZoneInfo("Europe/London"))

        middleware(request)

        # Should deactivate and return to default
        assert timezone.get_current_timezone() == timezone.get_default_timezone()

    def test_valid_timezone_cookie(self, middleware, request_factory):
        """With valid timezone cookie, should activate that timezone"""
        request = request_factory.get("/")
        request.COOKIES = {"timezone": "America/New_York"}

        middleware(request)

        # Check actual timezone is activated
        current_tz = timezone.get_current_timezone()
        assert isinstance(current_tz, ZoneInfo)
        assert str(current_tz) == "America/New_York"

    def test_invalid_timezone_cookie(self, middleware, request_factory):
        """With invalid timezone cookie, should fall back to default"""
        request = request_factory.get("/")
        request.COOKIES = {"timezone": "Invalid/Timezone"}

        # Set a known timezone first
        timezone.activate(ZoneInfo("Europe/London"))

        middleware(request)

        # Should deactivate due to invalid timezone
        assert timezone.get_current_timezone() == timezone.get_default_timezone()

    def test_response_is_returned(self, request_factory):
        """Middleware should return the response from get_response"""
        expected_response = Mock()

        def get_response(request):
            return expected_response

        middleware = TimezoneMiddleware(get_response)
        request = request_factory.get("/")
        request.COOKIES = {}

        response = middleware(request)
        assert response == expected_response

    def test_timezone_persists_during_request(self, request_factory):
        """Timezone should be active during request processing"""
        captured_timezone = None

        def get_response(request):
            nonlocal captured_timezone
            captured_timezone = timezone.get_current_timezone()
            return Mock()

        middleware = TimezoneMiddleware(get_response)
        request = request_factory.get("/")
        request.COOKIES = {"timezone": "Asia/Tokyo"}

        middleware(request)

        # Verify timezone was active during request
        assert isinstance(captured_timezone, ZoneInfo)
        assert str(captured_timezone) == "Asia/Tokyo"
