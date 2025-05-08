from django.db import models
from django.contrib.auth.models import User

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True



class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    summary = models.TextField(blank=True, null=True)
    experience = models.TextField(blank=True, null=True)
    education = models.TextField(blank=True, null=True)
    certifications = models.TextField(blank=True, null=True)
    languages = models.TextField(blank=True, null=True)



class Skills(BaseModel):
    name = models.CharField(max_length=100)
    profil = models.ManyToManyField(Profile, related_name="skills")



class Projects(BaseModel):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="projects", blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    technologies = models.TextField(blank=True, null=True)
    project_url = models.TextField(blank=True, null=True)



class Interview(BaseModel):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="interview")
    results = models.IntegerField(blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)


class InterviewQuestions(BaseModel):
    question = models.TextField(blank=True, null=True)
    user_answer = models.TextField(blank=True, null=True)
    correct_answer = models.TextField(blank=True, null=True)
    skill = models.ForeignKey(Skills, on_delete=models.CASCADE, related_name="questions", blank=True, null=True)
    interview = models.ForeignKey(Interview, on_delete=models.CASCADE, related_name="questions")



class Cv(BaseModel):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="cv")
    version_name = models.CharField(max_length=100, blank=True, null= True,)
    file = models.FileField(upload_to='cv/')
    content = models.TextField(blank=True, null= True)
    is_ai_generated = models.BooleanField(blank=True, null=False)



# ?: Should we add Cover Letters ??
