import random
import string


def generate_random_code(length: int = 4) -> str:
    """Generates random digits string
    :param length: length of the generated string
    :return: random digits string
    """
    digits = string.digits
    return ''.join(random.choice(digits) for _ in range(length))
