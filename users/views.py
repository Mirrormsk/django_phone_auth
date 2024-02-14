from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from users.models import User
from users.serializers import MyTokenObtainPairSerializer, UserSerializer, UserLoginSerializer, VerifyPhoneSerializer
from users.services.code_generator import generate_random_code
from users.services.get_token import get_tokens_for_user
from users.services.sms import send_verification_sms
from users.validators import validate_phone


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class LoginAPIView(APIView):
    serializer_class = UserLoginSerializer

    @staticmethod
    def get_object(phone: int):
        user, created = User.objects.get_or_create(phone=phone)
        if created:
            user.otp_code = generate_random_code()
            user.save()
        return user

    def post(self, request: Request, *args, **kwargs):

        phone = request.data.get('phone')
        phone = validate_phone(phone)

        user, created = User.objects.get_or_create(phone=phone)

        otp_code = generate_random_code()
        print(otp_code)
        user.otp_code = otp_code
        user.save()

        send_verification_sms(user)

        return Response({'message': 'Code was be sent by sms'}, status=status.HTTP_200_OK)


class VerifyAPIView(APIView):
    serializer_class = VerifyPhoneSerializer
    def post(self, request: Request, *args, **kwargs):

        serializer = VerifyPhoneSerializer(data=request.data)

        if serializer.is_valid():
            phone = serializer.validated_data["phone"]
            otp_code = serializer.validated_data["otp_code"]

            user = get_object_or_404(User, phone=phone)

            if user.otp_code and user.otp_code == otp_code:
                tokens = get_tokens_for_user(user)
                print(f'authorize {user}, tokens: {tokens}')
                user.otp_code = None
                user.save()
                return Response({'message': 'authorize successful', "tokens": tokens}, status=status.HTTP_200_OK)
            return Response({'message': 'Invalid code'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def perform_create(self, serializer):
        user = serializer.save()

        user.save()

    def get_serializer_class(self):

        if self.action == "retrieve":
            user = self.request.user
            instance = self.get_object()
            if instance == user:
                return UserSerializer
            return UserSerializer

        elif self.action == "list":
            return UserSerializer

        elif self.action in ["create", "update", "partial_update", "destroy"]:
            return UserSerializer

    def get_permissions(self):
        match self.action:
            case "create":
                permission_classes = [AllowAny]
            case _:
                permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
