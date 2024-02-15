from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.models import User
from users.validators import validate_phone


class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone']


class UserSerializer(serializers.ModelSerializer):
    """Serializer representing invited users"""
    invited_users = UserPublicSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = '__all__'


class UserLoginSerializer(serializers.Serializer):
    phone = serializers.CharField(
        max_length=12,
        style={'input_type': 'number', 'placeholder': 'Телефон'}
    )


class VerifyPhoneSerializer(serializers.Serializer):
    phone = serializers.CharField(validators=[validate_phone])
    otp_code = serializers.CharField()


class InputInviteCodeSerializer(serializers.Serializer):
    invite_code = serializers.CharField(max_length=6, min_length=6)


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user: User):
        token = super().get_token(user)
        token['first_name'] = user.first_name
        token['phone'] = user.phone

        return token



