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


# Todo: Check login func, Add email verfication, reset password, update user data, delete user,


class RegisterApiView(APIView):
    def post(self, request):
        data = request.data
        req_user = SignUpSerializer(data=data)

        if not req_user.is_valid():
            return Response(
                {"details": "not valid", "massage": req_user.errors},
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
                    "details": "email is not unique",
                    "massage": "There is already an account with this email.",
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
                    "details": "Password is weak",
                    "massage": "The password must contain at least one uppercase letter, one lowercase letter and a number.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        hashed_password = make_password(password=password)

        try:
            User.objects.create(
                email=email,
                username=username,
                password=hashed_password,
                first_name=first_name,
                last_name=last_name,
            )
        except DatabaseError as e:  # Todo: We can't show this error code to the user, but we need to store it somewhere, right?
            print(f"HATA: {e}")
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(
            {
                "details": "success",
                "massage": "Successfully created account. Please login.",
            },
            status=status.HTTP_201_CREATED,
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
                    "details": "success",
                    "massage": "Successfully logged out.",
                },
                status=status.HTTP_205_RESET_CONTENT,
            )
        except Exception:
            return Response(
                {
                    "details": "erorr",
                    "massage": "Logout failed. Please check the information and try again.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class CurrentUserApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = UserDataSerializer(request.user)
        return Response(
            {"details:": f"Kullanıcı = {user.data}"}, status=status.HTTP_200_OK
        )



# from datetime import datetime, timedelta
# from django.shortcuts import get_object_or_404
# from django.utils.crypto import get_random_string
# from .models import UserEmailToken
# class ForgotPasswordApiView(APIView):
#     def get(self, request):
#         data = request.data
#         user = get_object_or_404(User, data.get["email"])
#         token = get_random_string(40)
#         expire_date = datetime.now() + timedelta(minutes=10)

#         user.email_token.reset_password_token = token
#         user.email_token.reset_password_expire = expire_date
#         user.email_token.save()