from django.urls import path, include
from cvgen import views
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter



router = DefaultRouter()
router.register("profile", views.ProfileViewSet, basename="profile")
router.register("experience", views.ExperienceViewSet, basename="experience")
router.register("education", views.EducationViewSet, basename="education")
router.register("certification", views.CertificationViewSet, basename="certification")
router.register("language", views.LanguageViewSet, basename="language")
router.register("skill", views.SkillViewSet, basename="skill")
router.register("project", views.ProjectViewSet, basename="project")



urlpatterns = [
    path('upload_cv/', views.UploadCvApiView.as_view(), name='upload_cv'),
    path('analyze_cv/', views.AnalyzeCvWithAiApiView.as_view(), name='analyze_cv'),
    path('generate_cv/', views.GenerateCvPdfView.as_view(), name='generate_cv'),
    
    path('test/', views.TestApiViews.as_view(), name='test'), # Todo: Delete this before deploying


    path('', include(router.urls)),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)







