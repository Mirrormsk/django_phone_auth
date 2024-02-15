import datetime
from abc import ABC, abstractmethod
import logging
from django.conf import settings
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from users.models import User

logger = logging.getLogger(__name__)


class SMSService(ABC):
    """Abstract base class for SMS service"""

    @abstractmethod
    def send_sms(self, to: str, message: str) -> None:
        pass


class MySMSService(SMSService):
    """Fake SMS service"""
    def send_sms(self, to: str, message: str) -> None:
        print(f"Sending message to {to}: {message}")


def time_since_code_sent(user: User, now: datetime.datetime) -> datetime.timedelta:
    delta = now - user.last_code_sent_time
    return delta


def send_verification_sms(user: User, sms_service: SMSService) -> None:
    """Sends verification sms to user"""

    if not isinstance(sms_service, SMSService):
        raise AttributeError("SMS-Service must be an instance of SMSService")

    now = timezone.localtime(timezone.now())

    if user.last_code_sent_time:
        time_delta = time_since_code_sent(user, now)
        timeout = int(settings.SMS_VERIFICATION_RESEND_TIMEOUT)
        if time_delta.total_seconds() < timeout:
            time_remaining = int(timeout - time_delta.total_seconds())
            raise ValidationError(
                {"message": f"You can get new code after {time_remaining} seconds", "error": "Timeout not expired"})
    try:
        sms_service.send_sms(
            to=user.phone,
            message=f"Your verification code is {user.otp_code}"
        )
    except Exception as e:
        logger.exception(e)
    finally:
        user.last_code_sent_time = now
        user.save()
