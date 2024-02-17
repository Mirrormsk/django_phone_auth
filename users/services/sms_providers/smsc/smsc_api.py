from users.services.sms import AbstractSMSService
from users.services.sms_providers.smsc.smsc_module import SMSC


class SMSCService(AbstractSMSService):
    """Class for sending SMS through SMSC API"""

    def __init__(self):
        self.smsc_module = SMSC()

    def send_sms(self, to: str, message: str) -> None:
        """Send message"""
        self.smsc_module.send_sms(to, message)
