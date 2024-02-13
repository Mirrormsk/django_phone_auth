import datetime

from django.conf import settings
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from users.models import User


def time_since_code_sent(user: User, now: datetime.datetime) -> datetime.timedelta:
    delta = now - user.last_code_sent_time
    return delta


def send_verification_sms(user: User):
    now = timezone.localtime(timezone.now())

    if user.last_code_sent_time:
        time_delta = time_since_code_sent(user, now)
        timeout = int(settings.SMS_VERIFICATION_RESEND_TIMEOUT)
        if time_delta.total_seconds() < timeout:
            time_remaining = int(timeout - time_delta.total_seconds())
            raise ValidationError(
                {"message": f"You can get new code after {time_remaining} seconds", "error": "Timeout not expired"})

    user.last_code_sent_time = now
    user.save()
    print(f"phone: {user.phone}, code: {user.otp_code}")
