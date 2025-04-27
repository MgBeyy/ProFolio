from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


# Create your views here.
# Todo: ProfileViews from CV doc (Get, Post, Put, Delete)
# Todo: ProfileViews from FORM (Get, Post, Put, Delete)
# Todo: Cv generetor views
# Todo: interview init and questions views


class ProfileFromFormAPIViews(APIView):
    def get():
        pass

    def post():
        pass

    def put():
        pass

    def delete():
        pass
    


class TestApiViews(APIView):
    
    def get(self, request):
        return Response(status=status.HTTP_200_OK)

    def post(self, request):
        return Response(status=status.HTTP_201_CREATED)

    def put(self, request):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        return Response(status=status.HTTP_204_NO_CONTENT)
