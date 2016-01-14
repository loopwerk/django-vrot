from datetime import datetime, timedelta
from typing import Any, Optional, Union
from urllib.parse import urlencode

from django import template
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.template import Context
from django.template.defaultfilters import date
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import escape_uri_path
from django.utils.html import format_html
from django.utils.safestring import SafeString
from django.utils.timezone import localtime as _localtime

register = template.Library()


@register.simple_tag(takes_context=True)
def active_link(
    context: Context,
    viewname: str,
    css_class: str = "active",
    css_inactive_class: str = "",
    strict: bool = False,
) -> str:
    """
    Renders the given CSS class if the request path matches the path of the view.

    This tag is useful for highlighting active menu items in navigation. It compares
    the current request path with the URL of the given view name.

    Args:
        context: The template context where the tag was called. Used to access the request object.
        viewname: The name of the view (include namespaces if any).
        css_class: The CSS class to render if the view is active (default: "active").
        css_inactive_class: The CSS class to render if the view is not active (default: "").
        strict: If True, performs an exact match with the request path. If False,
                matches if the request path starts with the view's path (default: False).

    Returns:
        str: The appropriate CSS class based on whether the view is active.

    Example:
        {% active_link 'blog:index' 'active' 'inactive' %}
        {% active_link 'home' 'active' '' True %}
    """
    request = context.get("request")
    if request is None:
        # Can't work without the request object.
        return css_inactive_class

    active = False
    request_path = escape_uri_path(request.path)
    path = reverse(viewname.strip())

    if strict or path == "/":
        active = request_path == path
    else:
        active = request_path.startswith(path)

    return css_class if active else css_inactive_class


@register.filter
def getitem(array: Any, i: Any) -> Any:
    """
    Get a value from a list or dict by index/key.

    This filter allows dynamic access to dictionary values or list items in templates
    when the key/index is stored in a variable.

    Args:
        array: The list or dictionary to access.
        i: The index (for lists) or key (for dicts) to retrieve.

    Returns:
        The value at the given index/key, or empty string if not found.

    Example:
        {% load vrot %}
        {{ my_dict|getitem:my_key }}
        {{ my_list|getitem:0 }}
    """
    try:
        return array[i]
    except (IndexError, KeyError):
        return ""


@register.simple_tag(takes_context=True)
def query_param_replace(context: Context, **kwargs: Optional[Any]) -> str:
    """
    Replaces or adds query parameters while preserving existing ones.

    This is helpful for maintaining filter/search parameters while modifying
    specific parameters like page numbers in pagination.

    Args:
        context: The template context containing the request object.
        **kwargs: Key-value pairs of query parameters to add/update.
                 Use None as value to remove a parameter.

    Returns:
        str: A query string starting with '?' containing all parameters.

    Example:
        {% load vrot %}
        <a href="{% query_param_replace page=page_obj.previous_page_number %}">Previous</a>
        <a href="{% query_param_replace filter='active' page=1 %}">Active Items</a>
        <a href="{% query_param_replace filter=None %}">Clear Filter</a>
    """
    query = context["request"].GET.copy()
    for key, value in kwargs.items():
        if value is None:
            query.pop(key, None)
        else:
            query[key] = value

    return "?" + urlencode(query, doseq=True)


@register.filter
def localtime(value: Optional[datetime]) -> Union[str, SafeString]:
    """
    Renders a <time> element with ISO 8601 datetime that can be converted to local time via JavaScript.

    The rendered time element includes a 'local-time' class that the included JavaScript
    will use to convert the time to the user's local timezone.

    Args:
        value: A datetime object to format.

    Returns:
        str: HTML <time> element with datetime attribute and formatted display text,
             or empty string if value is None.

    Example:
        {{ comment.added|localtime }}

    Output:
        <time datetime="2024-05-19T10:34:00+02:00" class="local-time">May 19, 2024 at 10:34 AM</time>
    """
    if not value:
        return ""

    localized = _localtime(value)
    iso_format = date(localized, "c")

    # This format is specific to a US-style locale.
    display_format = date(localized, "F j, Y \\a\\t g:i A")

    return format_html('<time datetime="{}" class="local-time">{}</time>', iso_format, display_format)


@register.filter
def humantime(value: Optional[datetime]) -> Union[str, SafeString]:
    """
    Formats datetime in a human-friendly way based on how recent it is.

    - Less than 24 hours ago: Shows relative time (e.g., "2 hours ago")
    - 24-48 hours ago: Shows "Yesterday at X:XX AM/PM"
    - More than 48 hours ago: Uses the localtime filter for full date display

    Args:
        value: A datetime object to format.

    Returns:
        str: Human-friendly formatted time string, or empty string if value is None.

    Example:
        {{ comment.created_at|humantime }}
    """
    if not value:
        return ""

    now = timezone.now()
    localized = _localtime(value)
    time_diff = now - value

    # If `value` is less than 24 hours ago:
    if time_diff < timedelta(hours=24):
        return format_html('<span title="{}">{}</span>', date(localized, "g:i A"), naturaltime(localized))

    # If `value is less than 48 hours ago:
    if time_diff < timedelta(hours=48):
        return "Yesterday at " + date(localized, "g:i A")

    # Else:
    return localtime(value)
