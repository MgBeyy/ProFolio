from Scripts.ai_request import (
    parse_json_block,
    process_file_with_gemini,
    parse_date,
    send_prompt_to_gemini,
)
from cvgen import models, serializers
from cvgen.serializers import UploadCvSerializer
from helpers.ai_prompts import ANALYZE_CV_PROMPT, get_interview_prompt, get_answer_analysis_prompt, get_interview_feedback_prompt
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


class StartInterviewApiView(APIView):
    permission_classes = [IsAuthenticated]
    # TODO: What if the user has no skills?
    # TODO: What errors can occur and how to handle them?

    def get(self, request):
        try:
            user = request.user
            profile = models.Profile.objects.get(user=user)

            interview = models.Interview.objects.create(profile=profile)

            prompt = get_interview_prompt(profile.skills.all(), profile.language)

            ai_result = send_prompt_to_gemini(prompt_text=prompt)

            ai_result = parse_json_block(ai_result)

            question = ai_result.get("question")
            skill = models.Skill.objects.filter(
                profile=profile, name=ai_result.get("skill")
            ).first()

            interview_question = models.InterviewQuestion.objects.create(
                interview=interview, question=question, skill=skill
            )

            return Response(
                {
                    "result": "success",
                    "message": "Interview started successfully.",
                    "data": {
                        "interview_id": interview.id,
                        "question_id": interview_question.id,
                        "question": question,
                        "skill": skill.name,
                    },
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            print("EXCEPTION:", e)
            return Response(
                {
                    "result": "fail",
                    "message": "An error occurred, please try again.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )



class NextQuestionApiView(APIView):
    permission_classes = [IsAuthenticated]

    # TODO: What errors can occur and how to handle them?

    def post(self, request):
        try:
            user = request.user
            profile = models.Profile.objects.get(user=user)
            if request.data.get("interview_id"):
                if models.Interview.objects.filter(id=request.data.get("interview_id")).exists():
                    interview = models.Interview.objects.get(id=request.data.get("interview_id"))
                else:
                    return Response(
                        {
                            "result": "fail",
                            "message": "Interview not found.",
                        },
                        status=status.HTTP_404_NOT_FOUND,
                    )
            else:
                interview = models.Interview.objects.filter(profile=profile).order_by("-created_at").first()

            if not interview:
                return Response(
                    {
                        "result": "fail",
                        "message": "No interview found. Please start an interview first.",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
            
            if request.data.get("question_id"):
                if models.InterviewQuestion.objects.filter(id=request.data.get("question_id")).exists():
                    perv_question = models.InterviewQuestion.objects.get(id=request.data.get("question_id"))
                else:
                    return Response(
                        {
                            "result": "fail",
                            "message": "Question not found.",
                        },
                        status=status.HTTP_404_NOT_FOUND,
                    )
            else:
                perv_question = interview.questions.order_by("-created_at").first()

            if not perv_question:
                return Response(
                    {
                        "result": "fail",
                        "message": "No question found. Please start an interview first.",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            if request.data.get("answer"):
                answer = request.data.get("answer")
                prompt = get_answer_analysis_prompt(
                    question=perv_question.question,
                    answer=answer,
                    language=profile.language,
                )
                answer_analysis = send_prompt_to_gemini(
                    prompt_text=prompt,
                )
                answer_analysis = parse_json_block(answer_analysis)
                correct_part = answer_analysis.get("correct_part")
                wrong_part = answer_analysis.get("wrong_part")
                degree = answer_analysis.get("degree")
                perv_question.degree = degree
                perv_question.feedback = f"Correct part: {correct_part}\nWrong part: {wrong_part}"
                perv_question.save()
                feedback = {
                            "question": perv_question.question,
                            "correct_part": correct_part,
                            "wrong_part": wrong_part,
                            "degree": degree,
                        }
            else:
                feedback = None
            
            
            
            prompt = get_interview_prompt(profile.skills.all(), profile.language)

            ai_result = send_prompt_to_gemini(prompt_text=prompt)
            ai_result = parse_json_block(ai_result)

            next_question = ai_result.get("question")
            skill = models.Skill.objects.filter(
                profile=profile, name=ai_result.get("skill")
            ).first()

            interview_question = models.InterviewQuestion.objects.create(
                interview=interview, question=next_question, skill=skill
            )

            return Response(
                {
                    "result": "success",
                    "message": "Next question generated successfully.",
                    "data": {
                        "interview_id": interview.id,
                        "feedback": feedback,
                        "question_id": interview_question.id,
                        "question": next_question,
                        "skill": skill.name,
                    },
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            print("EXCEPTION:", e)
            return Response(
                {
                    "result": "fail",
                    "message": "An error occurred, please try again.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class FinishInterviewApiView(APIView):
    permission_classes = [IsAuthenticated]

    # TODO: What errors can occur and how to handle them?

    def post(self, request):
        try:
            user = request.user
            profile = models.Profile.objects.get(user=user)
            if request.data.get("interview_id"):
                if models.Interview.objects.filter(id=request.data.get("interview_id")).exists():
                    interview = models.Interview.objects.get(id=request.data.get("interview_id"))
                else:
                    return Response(
                        {
                            "result": "fail",
                            "message": "Interview not found.",
                        },
                        status=status.HTTP_404_NOT_FOUND,
                    )
            else:
                interview = models.Interview.objects.filter(profile=profile).order_by("-created_at").first()

            if not interview:
                return Response(
                    {
                        "result": "fail",
                        "message": "No interview found. Please start an interview first.",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
            
            if request.data.get("question_id"):
                if models.InterviewQuestion.objects.filter(id=request.data.get("question_id")).exists():
                    perv_question = models.InterviewQuestion.objects.get(id=request.data.get("question_id"))
                else:
                    return Response(
                        {
                            "result": "fail",
                            "message": "Question not found.",
                        },
                        status=status.HTTP_404_NOT_FOUND,
                    )
            else:
                perv_question = interview.questions.order_by("-created_at").first()

            if not perv_question:
                return Response(
                    {
                        "result": "fail",
                        "message": "No question found. Please start an interview first.",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            if request.data.get("answer"):
                answer = request.data.get("answer")
                prompt = get_answer_analysis_prompt(
                    question=perv_question.question,
                    answer=answer,
                    language=profile.language,
                )
                answer_analysis = send_prompt_to_gemini(
                    prompt_text=prompt,
                )
                answer_analysis = parse_json_block(answer_analysis)
                correct_part = answer_analysis.get("correct_part")
                wrong_part = answer_analysis.get("wrong_part")
                degree = answer_analysis.get("degree")
                perv_question.user_answer = answer
                perv_question.degree = degree
                perv_question.feedback = f"Correct part: {correct_part}\nWrong part: {wrong_part}"
                perv_question.save()
                feedback = {
                            "question": perv_question.question,
                            "correct_part": correct_part,
                            "wrong_part": wrong_part,
                            "degree": degree,
                        }
            else:
                feedback = None
            
            questions_and_answers = []
            for question in interview.questions.all():
                questions_and_answers.append({
                    "question": question.question,
                    "answer": question.user_answer,
                })
            
            
            prompt = get_interview_feedback_prompt(interview_questions=questions_and_answers, language=profile.language)

            ai_result = send_prompt_to_gemini(prompt_text=prompt)
            ai_result = parse_json_block(ai_result)

            positive_points = ai_result.get("positive_points")
            negative_points = ai_result.get("negative_points")
            score = ai_result.get("score")
            
            
            return Response(
                {
                    "result": "success",
                    "message": "Interview completed and feedback successfully generated.",
                    "data": {
                        "interview_id": interview.id,
                        "feedback": feedback,
                        "positive_points": positive_points,
                        "negative_points": negative_points,
                        "score": score,
                    },
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            print("EXCEPTION:", e)
            return Response(
                {
                    "result": "fail",
                    "message": "An error occurred, please try again.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


