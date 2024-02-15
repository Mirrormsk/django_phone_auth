from django.shortcuts import redirect
from django.views.generic import TemplateView
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.renderers import TemplateHTMLRenderer

from users.models import User
from users.serializers import MyTokenObtainPairSerializer, UserSerializer, UserLoginSerializer, VerifyPhoneSerializer, \
    InputInviteCodeSerializer
from users.services.code_generator import CodeGenerator
from users.services.get_token import get_tokens_for_user
from users.services.sms import send_verification_sms
from users.services.users import UserService
from users.validators import validate_phone


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class MyTokenRefreshView(TokenRefreshView):
    pass


class LoginAPIView(APIView):
    serializer_class = UserLoginSerializer

    def post(self, request: Request, *args, **kwargs):

        phone = request.data.get('phone')
        phone = validate_phone(phone)

        user, created = User.objects.get_or_create(phone=phone)

        if created:
            UserService.set_unique_invite_code(user)

        otp_code = UserService.set_otp_code(user)
        print(otp_code)
        send_verification_sms(user)

        return Response({'message': 'Code was be sent by sms', 'status': "success"}, status=status.HTTP_200_OK)


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
                user.otp_code = None
                user.is_active = True
                user.save()
                return Response({'message': 'authorize successful', "tokens": tokens, "status": "success"}, status=status.HTTP_200_OK)
            return Response({'message': 'Invalid code'}, status=status.HTTP_403_FORBIDDEN)
        else:
            print(serializer.errors)
            return Response({"message": "bad request"}, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

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

    @action(detail=True, methods=['post'])
    def input_invite(self, request, pk=None):
        user = self.get_object()

        serializer = InputInviteCodeSerializer(data=request.data)
        if serializer.is_valid():
            invite_code = serializer.validated_data.get('invite_code')
            referrer = UserService.find_user_by_invite_code(invite_code)
            if referrer:
                user.invited_by = referrer
                user.save()
                return Response({'message': 'Invite code successfully applied'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Invalid Invite Code'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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