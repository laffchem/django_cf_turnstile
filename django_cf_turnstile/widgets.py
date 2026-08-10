from django.forms import Widget
from django.conf import settings


class TurnstileWidget(Widget):
    template_name = "django_cf_turnstile/turnstile.html"

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"]["sitekey"] = getattr(settings, "TURNSTILE_SITEKEY", "")
        return context

    def value_from_datadict(self, data, fiels, name):
        return data.get("cf-turnstile-response", None)

