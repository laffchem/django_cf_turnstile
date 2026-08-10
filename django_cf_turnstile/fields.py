import niquests
from django.forms import Field, ValidationError
from django.conf import settings
from .widgets import TurnstileWidget

class TurnstileField(Field):
    widget = TurnstileWidget

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("required", True)
        super().__init__(*args, **kwargs)

    def clean(self, value):
        value = super().clean(value)

        if not value:
            return value
        
        secret = getattr(settings, "TURNSTILE_SECRET")
        if not secret:
            raise ValidationError("Turnstile secret key is not configured in your django settings")
        
        try:
            with niquests.Session() as s:
                response = s.post(
                    "https://challenges.cloudflare.com/turnstile/v0/siteverify",
                    data={'secret': secret, 'response': value},
                    timeout=5
                )
                result = response.json()
                if not result.get("success"):
                    raise ValidationError(
                        "Turnstile verification failed. Please try again."
                    )
        except niquests.exceptions.RequestException:
            raise ValidationError("Verification service is currently unavailable")
        
        return value