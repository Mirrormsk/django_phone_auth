from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.models import User
from users.services.code_generator import generate_random_code
from users.validators import validate_phone


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('phone', )


class VerifyPhoneSerializer(serializers.Serializer):
    phone = serializers.CharField(validators=[validate_phone])
    otp_code = serializers.CharField()


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user: User):
        token = super().get_token(user)
        token['first_name'] = user.first_name
        token['phone'] = user.phone

        return token


