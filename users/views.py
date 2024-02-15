from django.shortcuts import redirect
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.models import User
from users.permissions import IsOwner
from users.serializers import MyTokenObtainPairSerializer, UserSerializer, UserLoginSerializer, VerifyPhoneSerializer, \
    InputInviteCodeSerializer
from users.services.get_token import get_tokens_for_user
from users.services.sms import send_verification_sms, MySMSService
from users.services.users import UserService


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class MyTokenRefreshView(TokenRefreshView):
    pass


class LoginAPIView(APIView):
    serializer_class = UserLoginSerializer

    @swagger_auto_schema(
        request_body=UserLoginSerializer,
        responses={
            200: openapi.Response(
                description="Successful operation",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Сообщение'),
                        'status': openapi.Schema(type=openapi.TYPE_STRING, description='Статус операции'),
                        'otp_code': openapi.Schema(type=openapi.TYPE_STRING, description='Код подтверждения'),
                    },
                    required=['message', 'status'],
                ),
            ),

            400: openapi.Response(
                description="Bad request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING, description='Статус операции'),
                        'error': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING),
                                                description='Ошибки валидации'),
                    },
                    required=['status', 'error'],
                ),
            ),
        },
    )
    def post(self, request: Request, *args, **kwargs):

        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response({'status': "error", 'error': serializer.errors.values()},
                            status=status.HTTP_400_BAD_REQUEST)

        phone = serializer.validated_data.get('phone')

        user, created = User.objects.get_or_create(phone=phone)

        if created:
            UserService.set_unique_invite_code(user)

        otp_code = UserService.set_otp_code(user)

        sms_service = MySMSService()
        send_verification_sms(user, sms_service=sms_service)

        return Response({'message': 'Code was be sent by sms', 'status': "success", "otp_code": otp_code}, status=status.HTTP_200_OK)


class VerifyAPIView(APIView):
    serializer_class = VerifyPhoneSerializer

    @swagger_auto_schema(
        request_body=VerifyPhoneSerializer,
        responses={
            200: openapi.Response(
                description="Authorization successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Сообщение'),
                        'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID пользователя'),
                        'tokens': openapi.Schema(type=openapi.TYPE_OBJECT, description='Токены'),
                        'status': openapi.Schema(type=openapi.TYPE_STRING, description='Статус операции'),
                    },
                    required=['message', 'user_id', 'tokens', 'status'],
                ),
            ),
            403: openapi.Response(
                description="Invalid code",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Сообщение об ошибке'),
                    },
                    required=['message'],
                ),
            ),
        },
    )
    def post(self, request: Request, *args, **kwargs):

        serializer = VerifyPhoneSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({"message": "bad request", "status": "error", "error": serializer.errors.values()},
                            status=status.HTTP_400_BAD_REQUEST)

        phone = serializer.validated_data["phone"]
        otp_code = serializer.validated_data["otp_code"]

        user = get_object_or_404(User, phone=phone)

        if user.otp_code and user.otp_code == otp_code:
            tokens = get_tokens_for_user(user)
            user.otp_code = None
            user.is_active = True
            user.save()
            return Response({'message': 'authorize successful', "user_id": user.pk, "tokens": tokens, "status": "success"},
                            status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Invalid code'}, status=status.HTTP_403_FORBIDDEN)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsOwner]
    lookup_field = 'pk'

    @action(detail=True, methods=['post'])
    def input_invite(self, request, pk=None):
        user = self.get_object()

        if user.invited_by:
            return Response({'message': 'You are already have applied invite code'}, status=status.HTTP_403_FORBIDDEN)

        serializer = InputInviteCodeSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        invite_code = serializer.validated_data.get('invite_code')
        referrer = UserService.find_user_by_invite_code(invite_code)
        if referrer:
            user.invited_by = referrer
            user.save()
            return Response({'message': 'Invite code successfully applied'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Invalid Invite Code'}, status=status.HTTP_400_BAD_REQUEST)




class LoginView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'users/login.html'

    def get(self, request):
        serializer = UserLoginSerializer
        return Response({'serializer': serializer, 'verify_serializer': VerifyPhoneSerializer})

    def post(self, request, phone):
        user = get_object_or_404(User, phone=phone)
        serializer = UserLoginSerializer(user, data=request.data)
        verify_serializer = VerifyPhoneSerializer(data=request.data, initial={'phone': phone})

        if not serializer.is_valid():
            return Response({'status': "error", 'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Login successful'}, status=status.HTTP_200_OK)


class UserDetailView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    permission_classes = [IsAuthenticated]
    template_name = 'users/user_detail.html'

    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user)
        return Response({'serializer': serializer, 'user': user})

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user)
        if not serializer.is_valid():
            return Response({'serializer': serializer, 'user': user})
        serializer.save()
        return redirect('users:detail')
