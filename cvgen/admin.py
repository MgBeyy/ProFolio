from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Profile)
admin.site.register(Skills)
admin.site.register(Projects)
admin.site.register(Interview)
admin.site.register(InterviewQuestions)
admin.site.register(GeneratedCvs)