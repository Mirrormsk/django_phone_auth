from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import MyTokenObtainPairView, UserViewSet, LoginAPIView, VerifyAPIView
from users.apps import UsersConfig

app_name = UsersConfig.name

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="users")

urlpatterns = [
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('<int:pk>/detail/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('verify/', VerifyAPIView.as_view(), name='verify'),
] + router.urls
