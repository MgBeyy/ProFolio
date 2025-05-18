from Scripts.ai_request import parse_json_block, process_file_with_gemini, parse_date
from cvgen import models, serializers
from cvgen.serializers import UploadCvSerializer
from helpers.ai_prompts import ANALYZE_CV_PROMPT
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import viewsets
from django.template.loader import render_to_string
from django.http import HttpResponse
from Scripts.file_converter import convert_html_to_pdf

# Todo: Cv generator views
# Todo: interview init and questions views


class BaseUserRelatedViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_profile(self):
        return self.request.user.profile


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return models.Profile.objects.filter(user=self.request.user)


class ExperienceViewSet(BaseUserRelatedViewSet):
    serializer_class = serializers.ExperienceSerializer

    def get_queryset(self):
        return models.Experience.objects.filter(profile=self.get_profile())

    def perform_create(self, serializer):
        serializer.save(profile=self.get_profile())


class EducationViewSet(BaseUserRelatedViewSet):
    serializer_class = serializers.EducationSerializer

    def get_queryset(self):
        return models.Education.objects.filter(profile=self.get_profile())

    def perform_create(self, serializer):
        serializer.save(profile=self.get_profile())


class CertificationViewSet(BaseUserRelatedViewSet):
    serializer_class = serializers.CertificationSerializer

    def get_queryset(self):
        return models.Certification.objects.filter(profile=self.get_profile())

    def perform_create(self, serializer):
        serializer.save(profile=self.get_profile())


class LanguageViewSet(BaseUserRelatedViewSet):
    serializer_class = serializers.LanguageSerializer

    def get_queryset(self):
        return models.Language.objects.filter(profile=self.get_profile())

    def perform_create(self, serializer):
        serializer.save(profile=self.get_profile())


class SkillViewSet(BaseUserRelatedViewSet):
    serializer_class = serializers.SkillSerializer

    def get_queryset(self):
        return models.Skill.objects.filter(profile=self.get_profile())

    def perform_create(self, serializer):
        serializer.save(profile=self.get_profile())


class ProjectViewSet(BaseUserRelatedViewSet):
    serializer_class = serializers.ProjectSerializer

    def get_queryset(self):
        return models.Project.objects.filter(profile=self.get_profile())

    def perform_create(self, serializer):
        serializer.save(profile=self.get_profile())


class UploadCvApiView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]  # Todo: Add is_verified permission

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
        profile, _ = models.Profile.objects.get_or_create(user=user)
        cv.save(profile=profile, is_ai_generated=False)
        return Response(
            {
                "result": "success",
                "message": "File successfully uploaded.",
            },
            status=status.HTTP_200_OK,
        )


class AnalyzeCvWithAiApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile, _ = models.Profile.objects.get_or_create(user=user)
        cv_obj = (
            models.Cv.objects.filter(profile=profile).order_by("-created_at").first()
        )

        if not cv_obj or not cv_obj.file:
            return Response(
                {"result": "fail", "message": "CV file not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cv_file = cv_obj.file.path
        analyze_result = process_file_with_gemini(
            file_path=cv_file, prompt_text=ANALYZE_CV_PROMPT
        )
        parsed_result = parse_json_block(analyze_result)

        if parsed_result is None:
            return Response(
                {
                    "result": "fail",
                    "message": "An error occurred while parsing the result.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        try:
            profile.summary = parsed_result.get("summary", "")
            profile.save()

            models.Experience.objects.filter(profile=profile).delete()
            models.Education.objects.filter(profile=profile).delete()
            models.Certification.objects.filter(profile=profile).delete()
            models.Language.objects.filter(profile=profile).delete()
            models.Skill.objects.filter(profile=profile).delete()
            models.Project.objects.filter(profile=profile).delete()

            for exp in parsed_result.get("experience", []):
                models.Experience.objects.create(
                    profile=profile,
                    company=exp.get("company", ""),
                    position=exp.get("position", ""),
                    start_date=parse_date(exp.get("start_date", "")),
                    end_date=parse_date(exp.get("end_date", "")),
                    description=exp.get("description", ""),
                )

            for edu in parsed_result.get("education", []):
                models.Education.objects.create(
                    profile=profile,
                    school=edu.get("school", ""),
                    degree=edu.get("degree", ""),
                    start_date=parse_date(edu.get("start_date", "")),
                    end_date=parse_date(edu.get("end_date", "")),
                    description=edu.get("description", ""),
                )

            for cert in parsed_result.get("certifications", []):
                models.Certification.objects.create(
                    profile=profile,
                    name=cert.get("name", ""),
                    organization=cert.get("organization", ""),
                    start_date=parse_date(cert.get("start_date", "")),
                    end_date=parse_date(cert.get("end_date", "")),
                    description=cert.get("description", ""),
                )

            for lang in parsed_result.get("languages", []):
                models.Language.objects.create(
                    profile=profile,
                    language=lang.get("language", ""),
                    level=lang.get("level", ""),
                )

            for skill in parsed_result.get("skills", []):
                models.Skill.objects.create(
                    profile=profile,
                    name=skill.get("name", ""),
                    level=skill.get("level", ""),
                )

            for project in parsed_result.get("projects", []):
                models.Project.objects.create(
                    profile=profile,
                    title=project.get("title", ""),
                    description=project.get("description", ""),
                    technologies=project.get("technologies", ""),
                    project_url=project.get("project_url", ""),
                )

        except Exception:
            return Response(
                {"result": "fail", "message": "Error saving data."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"result": "success", "message": "Successfully analyzed the CV."},
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


class GenerateCvPdfView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.first_name is None or user.last_name is None:
            return Response(
                {"result": "fail", "message": "User name or last name is not set."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        
        profile = models.Profile.objects.get(user=user)
        experience = profile.experience.all()
        education = profile.education.all()
        certifications = profile.certifications.all()
        languages = profile.languages.all()
        skills = profile.skills.all()
        projects = profile.projects.all()

        context = {
            "profile": profile,
            "experience": experience,
            "education": education,
            "certifications": certifications,
            "languages": languages,
            "skills": skills,
            "projects": projects,
        }

        html_string = render_to_string("cv_template.html", context, request=request)
        pdf_content = convert_html_to_pdf(html_string)
        response = HttpResponse(pdf_content, content_type="application/pdf")
        response["Content-Disposition"] = "filename=converted.pdf"
        return response
