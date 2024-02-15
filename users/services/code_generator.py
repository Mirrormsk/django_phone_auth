import random
import string


class CodeGenerator:
    """Generates random digits string
    :param length: length of the generated string
    :param only_digits: if true code with only digits is generated
    :return: random digits string
    """
    def __init__(self, length: int = 4, only_digits: bool = True):
        self.length = length
        self.collection = string.digits

        if not only_digits:
            self.collection += string.ascii_letters

    def generate_random_code(self) -> str:
        return ''.join(random.choice(self.collection) for _ in range(self.length))

    def __call__(self, *args, **kwargs):
        return self.generate_random_code()
