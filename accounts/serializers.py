from rest_framework import serializers
from django.contrib.auth.models import User


class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "email", "password")

        extra_kwargs = {
            "email": {"required": True, "allow_blank": False},
            "password": {"write_only": True, "min_length": 8},
            "username": {"required": False, "allow_blank": True},
        }
