from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("register/", views.RegisterApiView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="refresh_token"),
    path("user/", views.UserApiView.as_view(), name="user"),
    path("logout/", views.LogoutApiView.as_view(), name="logout"),
    path("reset_password/", views.PasswordResetApiView.as_view(), name="reset_password"),
    path("verify_email/", views.VerifyEmailApiView.as_view(), name="verify_email"),
]
