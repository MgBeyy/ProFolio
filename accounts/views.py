from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework import status
from .serializers import SignUpSerializer
from django.db import DatabaseError

class RegisterApiView(APIView):
    def post(self, request):
        data = request.data
        req_user = SignUpSerializer(data = data)

        if not req_user.is_valid():
            return Response({"details": "not valid", 
                                "massage": req_user.errors}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        email = req_user.validated_data.get('email')
        username = email
        password = req_user.validated_data.get('password')
        first_name = req_user.validated_data.get('first_name')
        last_name = req_user.validated_data.get('last_name')
        
        if User.objects.filter(email=email).exists():
            return Response({"details": "email is not unique", 
                                "massage": "There is already an account with this email."}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        hashed_password = make_password(password=password)

        try:
            User.objects.create(email=email, username=username, password=hashed_password, first_name=first_name, last_name=last_name)
        except DatabaseError: # Todo: We can't show this error code to the user, but we need to store it somewhere, right?
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({"details": "success", 
                                "massage": "Successfully created account. Please login."}, status=status.HTTP_201_CREATED)


