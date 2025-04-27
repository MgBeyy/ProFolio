from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path('register/', views.RegisterApiView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token'),
]
