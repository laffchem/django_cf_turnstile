# django-cf-turnstile

A reusable Django app that integrates [Cloudflare Turnstile](https://www.cloudflare.com/products/turnstile/) into Django forms. Drop in a form field and widget, server-side verification is handled automatically. I wrote this for myself so I don't have to keep reimplimenting this at work.

## Requirements

- Python 3.13+
- Django 5.2+ (tested against 5.2 LTS and 6.0)

## Installation

```bash
uv add git+https://github.com/laffchem/django_cf_turnstile.git
```

Or pin to a specific tag:

```bash
uv add git+https://github.com/laffchem/django_cf_turnstile.git@v0.1.0
```

## Setup

### 1. Get your Turnstile keys

Go to the [Cloudflare Turnstile dashboard](https://dash.cloudflare.com/) and create a new site to obtain your **Site Key** and **Secret Key**.

### 2. Add your keys to Django settings

```python
# settings.py
TURNSTILE_SITEKEY = "your-site-key"
TURNSTILE_SECRET  = "your-secret-key"
```

## Usage

Add `TurnstileField` to any Django form:

```python
from django import forms
from django_cf_turnstile.fields import TurnstileField

class ContactForm(forms.Form):
    name    = forms.CharField()
    message = forms.CharField(widget=forms.Textarea)
    captcha = TurnstileField()
```

Render the form normally in your template:

```html
<form method="post">
	{% csrf_token %} {{ form.as_p }}
	<button type="submit">Send</button>
</form>
```

When the form is submitted, `TurnstileField.clean()` automatically posts the user's token to Cloudflare's verification endpoint and raises a `ValidationError` on failure — no extra code needed in your view.

## How it works

| Component         | Responsibility                                                                          |
| ----------------- | --------------------------------------------------------------------------------------- |
| `TurnstileWidget` | Renders the `<div class="cf-turnstile">` element and loads the Cloudflare JS            |
| `TurnstileField`  | Reads the `cf-turnstile-response` POST value and verifies it against the Cloudflare API |

The field POSTs to `https://challenges.cloudflare.com/turnstile/v0/siteverify` using [niquests](https://github.com/jawah/niquests) with a 5-second timeout. Network errors surface as a user-friendly `ValidationError` rather than an unhandled exception.

## Running the tests

Tests use [pytest](https://docs.pytest.org/) and [pytest-django](https://pytest-django.readthedocs.io/):

```bash
uv run --group dev pytest
```

To run the full suite against every supported Django version (5.2 and 6.0), use [tox](https://tox.wiki/):

```bash
uv tool install tox --with tox-uv
tox
```

CI runs this same matrix on every push and pull request via [.github/workflows/tests.yml](.github/workflows/tests.yml).

## License

MIT [LICENSE](LICENSE).
