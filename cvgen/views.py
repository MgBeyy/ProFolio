from Scripts.ai_request import parse_json_block, process_file_with_gemini
from cvgen.models import Cv, Profile
from cvgen.serializers import UploadCvSerializer
from helpers.ai_prompts import ANALYZE_CV_PROMPT
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

# Create your views here.
# Todo: ProfileViews from CV doc (Get, Post, Put, Delete)
# Todo: ProfileViews from FORM (Get, Post, Put, Delete)
# Todo: Cv generetor views
# Todo: interview init and questions views


class UploadCvApiView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated] # Todo: Add is_verified permission

    def post(self, request):
        cv = UploadCvSerializer(data=request.data)
        if not cv.is_valid():
            return Response(
            {
                "result": "fail",
                "message": f"File is not valid. Error: {cv.errors}",
            },
            status=status.HTTP_400_BAD_REQUEST,
            )
        user = request.user
        profile, _ = Profile.objects.get_or_create(user=user)
        cv.save(profile=profile, is_ai_generated=False)
        return Response(
            {
                "result": "success",
                "message": "File successfly uploaded.",
            },
            status=status.HTTP_200_OK,
            )


class AnalyzeCvWithAiApiView(APIView):
    
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile = user.profile
        cv_obj = Cv.objects.filter(profile=profile).first()
        cv_file = cv_obj.file.path
        

        analyze_result = process_file_with_gemini(file_path=cv_file, prompt_text=ANALYZE_CV_PROMPT)


        parsed_result = parse_json_block(analyze_result)

        if parsed_result is None:
            return Response(
            {
            "result": "fail",
            "message": "An error occurred while parsing the result.",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        data = parsed_result
        return Response(
        {
            "result": "success",
            "data": data,
        },
        status=status.HTTP_200_OK,
        )


class TestApiViews(APIView):
    
    def get(self, request):
        return Response(status=status.HTTP_200_OK)

    def post(self, request):
        return Response(status=status.HTTP_201_CREATED)

    def put(self, request):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        return Response(status=status.HTTP_204_NO_CONTENT)
