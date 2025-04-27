from django.urls import path
from cvgen import views

urlpatterns = [
    path('profile/', views.ProfileFromFormAPIViews.as_view(), name='profile_from_form'), # Todo: Change 'profile/' for more readability. 
    
    
    path('test/', views.TestApiViews.as_view(), name='test'), # Todo: Delete this before deploying
]

