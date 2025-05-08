from django.contrib import admin
from cvgen import models

# Register your models here.
admin.site.register(models.Profile)
admin.site.register(models.Skills)
admin.site.register(models.Projects)
admin.site.register(models.Interview)
admin.site.register(models.InterviewQuestions)
admin.site.register(models.Cv)