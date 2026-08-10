import niquests
import pytest
from django import forms
from django.core.exceptions import ValidationError

from django_cf_turnstile.fields import TurnstileField


class DummyForm(forms.Form):
    turnstile = TurnstileField()


def test_clean_raises_error_if_secret_missing(settings):
    """Ensure the field fails if the developer forgot to add the secret to settings"""
    settings.TURNSTILE_SECRET = ""
    field = TurnstileField()
    with pytest.raises(ValidationError, match="Turnstile secret key is not configured"):
        field.clean("some_token")


@pytest.mark.parametrize(
    "cf_response,is_valid",
    [
        ({"success": True}, True),
        ({"success": False, "error-codes": ["invalid-input-response"]}, False),
    ],
    ids=["success", "invalid_token"],
)
def test_clean_against_cloudflare_response(settings, mock_post, cf_response, is_valid):
    """Ensure the field's outcome matches what Cloudflare's siteverify API reports."""
    settings.TURNSTILE_SECRET = "fake_secret_key"
    mock_post.return_value.json.return_value = cf_response

    field = TurnstileField()
    if is_valid:
        assert field.clean("valid_cloudflare_token") == "valid_cloudflare_token"
    else:
        with pytest.raises(ValidationError, match="Turnstile verification failed"):
            field.clean("invalid_token")

    mock_post.assert_called_once()
    called_kwargs = mock_post.call_args.kwargs
    assert called_kwargs["data"]["secret"] == "fake_secret_key"


def test_clean_fails_gracefully_on_network_timeout(settings, mock_post):
    """Ensure the field doesn't crash the server if cloudflare is down"""
    settings.TURNSTILE_SECRET = "fake_secret_key"
    mock_post.side_effect = niquests.exceptions.RequestException("DNS lookup failed")

    field = TurnstileField()
    with pytest.raises(
        ValidationError, match="Verification service is currently unavailable"
    ):
        field.clean("some_token")


def test_form_integration(settings, mock_post):
    """Test the field end-to-end within a django form"""
    settings.TURNSTILE_SECRET = "fake_secret_key"
    mock_post.return_value.json.return_value = {"success": True}

    form = DummyForm({"cf-turnstile-response": "valid_token"})

    assert form.is_valid()
    assert form.cleaned_data["turnstile"] == "valid_token"
