from Scripts.host_data import get_current_host_url
from accounts.models import UserEmailToken
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import SignUpSerializer, UserDataSerializer
from django.db import DatabaseError
import re
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta
from django.utils import timezone
from django.utils.crypto import get_random_string
from Scripts.mail import send_mail_via_mailgun


# Todo: update user data, delete user


class RegisterApiView(APIView):
    def post(self, request):
        data = request.data
        req_user = SignUpSerializer(data=data)

        if not req_user.is_valid():
            return Response(
                {
                    "result": "fail",
                    "message": req_user.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = req_user.validated_data.get("email")
        username = email
        password = req_user.validated_data.get("password")
        first_name = req_user.validated_data.get("first_name")
        last_name = req_user.validated_data.get("last_name")

        if User.objects.filter(email=email).exists():
            return Response(
                {
                    "result": "fail",
                    "message": "There is already an account with this email.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not first_name:
            first_name = " "

        if not last_name:
            last_name = " "

        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$"
        if not re.match(pattern, password):
            return Response(
                {
                    "result": "fail",
                    "message": "The password must contain at least one uppercase letter, one lowercase letter and a number.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        hashed_password = make_password(password=password)

        try:
            user = User.objects.create(
                email=email,
                username=username,
                password=hashed_password,
                first_name=first_name,
                last_name=last_name,
            )
        except DatabaseError as e:  # Todo: We can't show this error code to the user, but we need to store it somewhere, right?
            print(f"HATA: {e}")
            return Response(
                {
                    "result": "fail",
                    "message": "Failed to create an account. Please try again later.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Email verification

        user_token = UserEmailToken.objects.create(
            user=user,
            email_verification_token=get_random_string(40),
            email_verification_expire=timezone.now() + timedelta(minutes=10),
            is_verified=False,
        )

        host = get_current_host_url(request)

        is_sent, response = send_mail_via_mailgun(
            to_email=user.email,
            subject="Email Verification For ProFolio",
            message="Please click on the link to verify your email: \n "
            f"{host}verify_email?token={user_token.email_verification_token}",
        )

        if is_sent:
            return Response(
                {
                    "result": "success",
                    "message": "Successfully created account. Please check your email inbox to verify the email.",
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {
                    "result": "fail",
                    "message": "The account was created but the verification email could not be sent. Please try again later.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# ? Does this really work? How can we be sure??
class LogoutApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            r_token = RefreshToken(refresh_token)
            r_token.blacklist()
            return Response(
                {
                    "result": "success",
                    "message": "Successfully logged out.",
                },
                status=status.HTTP_205_RESET_CONTENT,
            )
        except Exception:
            return Response(
                {
                    "result": "fail",
                    "message": "Logout failed. Please check the information and try again.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class CurrentUserApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = UserDataSerializer(request.user)
        return Response(
            {
                "result": "fail",
                "message": f"Kullanıcı = {user.data}",
            },
            status=status.HTTP_200_OK,
        )


class VerifyEmailApiView(APIView):
    def get(self, request):
        token = request.query_params.get("token")

        if not UserEmailToken.objects.filter(email_verification_token=token).exists():
            return Response(
                {
                    "result": "fail",
                    "message": "This verification link is invalid.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        email_token = UserEmailToken.objects.filter(
            email_verification_token=token
        ).first()

        if email_token.email_verification_expire < timezone.now():
            return Response(
                {
                    "result": "fail",
                    "message": "This verification link has expired.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        email_token.email_verification_token = ""
        email_token.is_verified = True
        email_token.save()

        return Response(
            {
                "result": "success",
                "message": "Email successfully verified.",
            },
            status=status.HTTP_200_OK,
        )


class PasswordResetApiView(APIView):
    def get(self, request):
        email = request.data.get("email")

        if not User.objects.filter(email=email).exists():
            return Response(
                {
                    "result": "fail",
                    "message": "There is no account with this email. Please register first.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(email=email).first()

        user_token, _ = UserEmailToken.objects.get_or_create(user=user)

        user_token.reset_password_token = get_random_string(40)
        user_token.reset_password_expire = timezone.now() + timedelta(minutes=10)
        user_token.save()

        host = get_current_host_url(request)

        is_sent, response = send_mail_via_mailgun(
            to_email=user.email,
            subject="Reset Password For ProFolio",
            message="Please click on the link to reset your password: \n "
            f"{host}reset_password?token={user_token.reset_password_token}",
        )

        if is_sent:
            return Response(
                {
                    "result": "success",
                    "message": "The password reset email was sent successfully. Please check your email inbox and click on the link in the email.",
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {
                    "result": "fail",
                    "message": "The password reset email could not be sent. Please try again later.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class PasswordResetConfirmApiView(APIView):
    def get(self, request):
        token = request.query_params.get("token")

        if not UserEmailToken.objects.filter(reset_password_token=token).exists():
            return Response(
                {
                    "result": "fail",
                    "message": "This password reset link is invalid.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        email_token = UserEmailToken.objects.filter(reset_password_token=token).first()

        if email_token.reset_password_expire < timezone.now():
            return Response(
                {
                    "result": "fail",
                    "message": "This password reset link has expired.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "result": "success",
                "message": "Link is valid. Please put your new password.",
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request):
        token = request.query_params.get("token")

        if not UserEmailToken.objects.filter(reset_password_token=token).exists():
            return Response(
                {
                    "result": "fail",
                    "message": "This password reset link is invalid.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        email_token = UserEmailToken.objects.filter(reset_password_token=token).first()

        if email_token.reset_password_expire < timezone.now():
            return Response(
                {
                    "result": "fail",
                    "message": "This password reset link has expired.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        password = request.data.get("password")
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$"
        if not re.match(pattern, password):
            return Response(
                {
                    "result": "fail",
                    "message": "The password must contain at least one uppercase letter, one lowercase letter and a number.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        email_token.reset_password_token = ""
        email_token.save()

        user = email_token.user
        hashed_password = make_password(password=password)
        user.password = hashed_password
        user.save()

        return Response(
            {
                "result": "success",
                "message": "Password reset successfully.",
            },
            status=status.HTTP_200_OK,
        )
