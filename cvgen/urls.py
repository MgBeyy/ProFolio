from django.urls import path
from cvgen import views

urlpatterns = [
    path('', views.ProfileFromFormAPIViews.as_view(), name='profile_from_form'),
]

