# django-vrot

A collection of Django templatetags and middleware for common web development tasks.

## Features

- **Local timezone display**: Automatically display dates and times in the visitor's local timezone
- **Active link detection**: Highlight active menu items based on current URL
- **Query parameter management**: Easily modify query parameters while preserving others
- **Template utilities**: Access dictionary items dynamically and format time displays

## Installation

```bash
uv add django-vrot
```

## Quick Start

1. Add `vrot` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    "vrot",
]
```

2. For timezone support, add the middleware to your `MIDDLEWARE`:

```python
MIDDLEWARE = [
    # ...
    "vrot.middleware.TimezoneMiddleware",
]
```

3. Include the JavaScript file in your base template (only needed for timezone features):

```html
{% load static %}
<script src="{% static 'vrot/timezone.js' %}" defer></script>
```

## Usage

### Template Tags

Load the template tags in your templates:

```django
{% load vrot %}
```

#### `localtime` - Display times in user's timezone

Renders a time element that will be converted to the user's local timezone via JavaScript:

```django
{{ comment.created_at|localtime }}
```

Output:

```html
<time datetime="2024-05-19T10:34:00+02:00" class="local-time">May 19, 2024 at 10:34 AM</time>
```

#### `humantime` - Human-friendly time display

Shows relative time for recent dates:

```django
{{ comment.created_at|humantime }}
```

Outputs:

- "2 hours ago" (for times less than 24 hours ago)
- "Yesterday at 3:45 PM" (for times 24-48 hours ago)
- Full date display (for older times)

#### `active_link` - Highlight active menu items

```django
<li class="{% active_link 'blog:index' %}">
    <a href="{% url 'blog:index' %}">Blog</a>
</li>
```

Parameters:

- `viewname`: The name of the view (including namespace, if any)
- `css_class`: CSS class to apply when active (default: "menu-active")
- `css_inactive_class`: CSS class when inactive (default: "")
- `strict`: If True, requires exact path match (default: False)

#### `query_param_replace` - Preserve query parameters

Useful for pagination while maintaining filters:

```django
<a href="{% query_param_replace page=page_obj.next_page_number %}">Next Page</a>
```

This preserves existing query parameters (like filters) while updating the page number.

#### `getitem` - Access dictionary/list items

Access dictionary values with dynamic keys:

```django
{{ my_dict|getitem:user_provided_key }}
```

### Middleware

#### TimezoneMiddleware

Automatically activates the user's timezone based on a cookie set by the JavaScript code. This allows Django to render times in the user's local timezone server-side.

The middleware reads the `timezone` cookie and activates the corresponding timezone for the duration of the request.

## How Local Timezone Display Works

1. The included JavaScript sets a cookie with the user's timezone
2. The `TimezoneMiddleware` reads this cookie and activates the timezone in Django
3. The `localtime` filter renders times with proper timezone information
4. The JavaScript converts any remaining times to the user's local format

For more details, see: https://www.loopwerk.io/articles/2025/django-local-times/

## Requirements

- Django >= 3.2
- Python >= 3.9

## License

MIT License - see LICENSE file for details.
