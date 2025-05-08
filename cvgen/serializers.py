from rest_framework import serializers
from .models import Profile, Cv
import os


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'


class UploadCvSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cv
        fields = ["file", "version_name"]
        read_only_fields = ["created_at", "updated_at"]

        extra_kwargs = {
            "version_name": {"required": False, "allow_blank": True},
        }
    
    def validate_file(self, value):
        ext = os.path.splitext(value.name)[1]
        valid_extensions = ['.pdf', '.docx']
        if ext.lower() not in valid_extensions:
            raise serializers.ValidationError('Only PDF and DOCX files are accepted.')
        return value
