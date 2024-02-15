from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import MyTokenObtainPairView, UserViewSet, LoginAPIView, VerifyAPIView, MyTokenRefreshView, LoginView, \
    UserDetailView
from users.apps import UsersConfig

app_name = UsersConfig.name

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="users")

urlpatterns = [
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', MyTokenRefreshView.as_view(), name='token_refresh'),
    path('api/login/', LoginAPIView.as_view(), name='api_login'),
    path('verify/', VerifyAPIView.as_view(), name='verify'),
    path("login/", LoginView.as_view(), name="login"),
    path("detail/<int:pk>", UserDetailView.as_view(), name="detail")
] + router.urls
