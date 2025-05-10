from django.urls import path
from cvgen import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('upload_cv/', views.UploadCvApiView.as_view(), name='upload_cv'),
    path('analyze_cv/', views.AnalyzeCvWithAiApiView.as_view(), name='analyze_cv'),
    
    path('test/', views.TestApiViews.as_view(), name='test'), # Todo: Delete this before deploying
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

