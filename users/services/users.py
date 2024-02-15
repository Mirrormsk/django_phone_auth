from users.models import User
from users.services.code_generator import CodeGenerator


class UserService:

    @classmethod
    def find_user_by_invite_code(cls, invite_code: str) -> User | None:
        return User.objects.filter(invite_code=invite_code).first()

    @classmethod
    def set_unique_invite_code(cls, user: User) -> str:
        """Generates and set unique invite code"""
        invite_code_generator = CodeGenerator(length=6, only_digits=False)
        invite_code = invite_code_generator()

        while invite_code in User.objects.all().values_list('invite_code', flat=True):
            invite_code = invite_code_generator()

        user.invite_code = invite_code
        user.save()

        return invite_code

    @classmethod
    def set_otp_code(cls, user: User) -> str:
        """Generates and set otp code for user"""
        generator = CodeGenerator(4)
        otp_code = generator()

        user.otp_code = otp_code
        user.save()
        return otp_code
