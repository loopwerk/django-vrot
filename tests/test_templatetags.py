import datetime
from unittest.mock import patch

import pytest
from django.template import Context, Template
from django.test import RequestFactory
from django.utils import timezone
from freezegun import freeze_time


@pytest.fixture
def request_factory():
    return RequestFactory()


class TestActiveLink:
    def test_active_link_exact_match(self, request_factory):
        request = request_factory.get("/blog/")
        context = Context({"request": request})

        with patch("vrot.templatetags.vrot.reverse", return_value="/blog/"):
            template = Template('{% load vrot %}{% active_link "blog:index" "active" "" True %}')
            result = template.render(context)
            assert result == "active"

    def test_active_link_no_exact_match(self, request_factory):
        request = request_factory.get("/blog/post/1/")
        context = Context({"request": request})

        with patch("vrot.templatetags.vrot.reverse", return_value="/blog/"):
            template = Template('{% load vrot %}{% active_link "blog:index" "active" "" True %}')
            result = template.render(context)
            assert result == ""

    def test_active_link_prefix_match(self, request_factory):
        request = request_factory.get("/blog/post/1/")
        context = Context({"request": request})

        with patch("vrot.templatetags.vrot.reverse", return_value="/blog/"):
            template = Template('{% load vrot %}{% active_link "blog:index" "active" %}')
            result = template.render(context)
            assert result == "active"

    def test_active_link_root_strict(self, request_factory):
        request = request_factory.get("/about/")
        context = Context({"request": request})

        with patch("vrot.templatetags.vrot.reverse", return_value="/"):
            template = Template('{% load vrot %}{% active_link "home" "active" %}')
            result = template.render(context)
            assert result == ""

    def test_active_link_with_inactive_class(self, request_factory):
        request = request_factory.get("/about/")
        context = Context({"request": request})

        with patch("vrot.templatetags.vrot.reverse", return_value="/blog/"):
            template = Template('{% load vrot %}{% active_link "blog:index" "active" "inactive" %}')
            result = template.render(context)
            assert result == "inactive"

    def test_active_link_no_request(self):
        context = Context({})
        template = Template('{% load vrot %}{% active_link "blog:index" "active" "inactive" %}')
        result = template.render(context)
        assert result == "inactive"


class TestGetitem:
    def test_getitem_dict(self):
        context = Context({"my_dict": {"key": "value"}, "my_key": "key"})
        template = Template("{% load vrot %}{{ my_dict|getitem:my_key }}")
        result = template.render(context)
        assert result == "value"

    def test_getitem_list(self):
        context = Context({"my_list": ["a", "b", "c"], "index": 1})
        template = Template("{% load vrot %}{{ my_list|getitem:index }}")
        result = template.render(context)
        assert result == "b"

    def test_getitem_missing_key(self):
        context = Context({"my_dict": {"key": "value"}, "my_key": "missing"})
        template = Template("{% load vrot %}{{ my_dict|getitem:my_key }}")
        result = template.render(context)
        assert result == ""

    def test_getitem_index_error(self):
        context = Context({"my_list": ["a", "b"], "index": 5})
        template = Template("{% load vrot %}{{ my_list|getitem:index }}")
        result = template.render(context)
        assert result == ""


class TestQueryParamReplace:
    def test_query_param_replace_add(self, request_factory):
        request = request_factory.get("/search/?q=test")
        context = Context({"request": request})
        template = Template("{% load vrot %}{% query_param_replace page=2 %}")
        result = template.render(context)
        assert "q=test" in result
        assert "page=2" in result

    def test_query_param_replace_update(self, request_factory):
        request = request_factory.get("/search/?page=1&q=test")
        context = Context({"request": request})
        template = Template("{% load vrot %}{% query_param_replace page=2 %}")
        result = template.render(context)
        assert "page=2" in result
        assert "q=test" in result
        assert "page=1" not in result

    def test_query_param_replace_remove(self, request_factory):
        request = request_factory.get("/search/?page=1&q=test")
        context = Context({"request": request})
        template = Template("{% load vrot %}{% query_param_replace page=None %}")
        result = template.render(context)
        assert "page=" not in result
        assert "q=test" in result

    def test_query_param_replace_empty(self, request_factory):
        request = request_factory.get("/search/")
        context = Context({"request": request})
        template = Template("{% load vrot %}{% query_param_replace page=1 %}")
        result = template.render(context)
        assert result == "?page=1"


class TestLocaltime:
    def test_localtime_filter(self):
        # Create a timezone-aware datetime in UTC
        dt = datetime.datetime(2024, 5, 19, 8, 34, 0, tzinfo=datetime.timezone.utc)
        context = Context({"dt": dt})
        template = Template("{% load vrot %}{{ dt|localtime }}")
        result = template.render(context)

        assert '<time datetime="2024-05-19T08:34:00+00:00" class="local-time">' in result
        assert "May 19, 2024 at 8:34 AM</time>" in result

    def test_localtime_filter_none(self):
        context = Context({"dt": None})
        template = Template("{% load vrot %}{{ dt|localtime }}")
        result = template.render(context)
        assert result == ""

    def test_localtime_filter_with_timezone(self):
        # Create a timezone-aware datetime with +2 offset
        dt = datetime.datetime(2024, 5, 19, 15, 45, 0, tzinfo=datetime.timezone(datetime.timedelta(hours=2)))
        context = Context({"dt": dt})
        template = Template("{% load vrot %}{{ dt|localtime }}")
        result = template.render(context)

        # Django converts to UTC when USE_TZ=True and TIME_ZONE='UTC'
        assert '<time datetime="2024-05-19T13:45:00+00:00" class="local-time">' in result
        assert "May 19, 2024 at 1:45 PM</time>" in result


class TestHumantime:
    @freeze_time("2024-05-19 10:00:00", tz_offset=0)
    def test_humantime_recent(self):
        # Time 2 hours ago
        dt = timezone.now() - datetime.timedelta(hours=2)
        context = Context({"dt": dt})
        template = Template("{% load vrot %}{{ dt|humantime }}")
        result = template.render(context)

        assert '<span title="8:00 AM">' in result
        # naturaltime uses non-breaking space (\\xa0)
        assert "2\xa0hours ago</span>" in result

    @freeze_time("2024-05-19 10:00:00", tz_offset=0)
    def test_humantime_yesterday(self):
        # Time 30 hours ago (yesterday)
        dt = timezone.now() - datetime.timedelta(hours=30)
        context = Context({"dt": dt})
        template = Template("{% load vrot %}{{ dt|humantime }}")
        result = template.render(context)

        assert "Yesterday at 4:00 AM" in result

    @freeze_time("2024-05-19 10:00:00", tz_offset=0)
    def test_humantime_old(self):
        # Time 3 days ago
        dt = timezone.now() - datetime.timedelta(days=3)
        context = Context({"dt": dt})
        template = Template("{% load vrot %}{{ dt|humantime }}")
        result = template.render(context)

        # Should use localtime filter for older dates
        assert "<time datetime=" in result
        assert 'class="local-time"' in result

    def test_humantime_none(self):
        context = Context({"dt": None})
        template = Template("{% load vrot %}{{ dt|humantime }}")
        result = template.render(context)
        assert result == ""
