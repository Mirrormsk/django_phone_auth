from rest_framework.exceptions import ValidationError


def validate_phone(phone: str):
    if phone.startswith('+'):
        phone = phone[1:]
    if phone.startswith('8'):
        phone = f"7{phone[1:]}"

    if len(phone) < 11:
        raise ValidationError("Phone number length must be at least 11 digits")
    elif not phone.isdigit():
        raise ValidationError("Phone number must contain only digits or '+' and digits")

    return phone


