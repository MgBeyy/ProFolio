from rest_framework import serializers
from cvgen import models
import os


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Profile
        fields = "__all__"


class UploadCvSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Cv
        fields = ["file", "version_name"]
        read_only_fields = ["created_at", "updated_at"]

        extra_kwargs = {
            "version_name": {"required": False, "allow_blank": True},
        }

    def validate_file(self, value):
        ext = os.path.splitext(value.name)[1]
        valid_extensions = [".pdf", ".docx"]
        if ext.lower() not in valid_extensions:
            raise serializers.ValidationError("Only PDF and DOCX files are accepted.")
        return value


class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Experience
        fields = "__all__"


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Education
        fields = "__all__"


class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Certification
        fields = "__all__"


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Language
        fields = "__all__"


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Skill
        fields = "__all__"


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Project
        fields = "__all__"
