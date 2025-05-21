from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    summary = models.TextField(blank=True, null=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    prof_email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    github = models.URLField(blank=True, null=True)
    language = models.CharField(max_length=100, blank=True, null=True) # Language of the interview questions
    

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Experience(BaseModel):
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="experience"
    )
    company = models.CharField(max_length=100, blank=True, null=True)
    position = models.CharField(max_length=100, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.position} at {self.company}"


class Education(BaseModel):
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="education"
    )
    school = models.CharField(max_length=100, blank=True, null=True)
    degree = models.CharField(max_length=100, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.degree} at {self.school}"


class Certification(BaseModel):
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="certifications"
    )
    name = models.CharField(max_length=100, blank=True, null=True)
    organization = models.CharField(max_length=100)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} by {self.organization}"


class Language(BaseModel):
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="languages"
    )
    language = models.CharField(max_length=100, blank=True, null=True)
    level = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.language} ({self.level})"


class Skill(BaseModel):
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="skills"
    )
    name = models.CharField(max_length=100, blank=True, null=True)
    level = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.level})"


class Project(BaseModel):
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="projects"
    )
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    technologies = models.TextField(blank=True, null=True)
    project_url = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title


class Interview(BaseModel):
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="interview"
    )
    results = models.IntegerField(blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Interview for {self.profile.user.username}"


class InterviewQuestion(BaseModel):
    question = models.TextField(blank=True, null=True)
    user_answer = models.TextField(blank=True, null=True)
    correct_answer = models.TextField(blank=True, null=True)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="questions")
    interview = models.ForeignKey(
        Interview, on_delete=models.CASCADE, related_name="questions"
    )

    def __str__(self):
        return f"Question about {self.skill.name}"


class Cv(BaseModel):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="cv")
    version_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )
    file = models.FileField(upload_to="cv/")
    content = models.TextField(blank=True, null=True)
    is_ai_generated = models.BooleanField(blank=True, null=False)

    def __str__(self):
        return f"{self.profile.user.username}'s CV - {self.version_name or 'Default'}"


# ?: Should we add Cover Letters ??
