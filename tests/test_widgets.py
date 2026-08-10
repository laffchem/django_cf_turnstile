from django_cf_turnstile.widgets import TurnstileWidget


def test_widget_context_contains_sitekey(settings):
    """Ensure widget is correctly pulling sitekey from settings into context"""
    settings.TURNSTILE_SITEKEY = "fake_site_key_123"
    widget = TurnstileWidget()

    context = widget.get_context("turnstile", None, {})
    assert context["widget"]["sitekey"] == "fake_site_key_123"


def test_value_from_datadict():
    """Ensure the widget specifically looks for the cf-turnstile response."""
    widget = TurnstileWidget()
    mock_post_data = {
        "other_field": "hello",
        "cf-turnstile-response": "intercepted_token",
    }
    value = widget.value_from_datadict(mock_post_data, None, "turnstile")
    assert value == "intercepted_token"
