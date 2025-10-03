from django.urls import path
from .views import TeacherAuthLoginView, StudentAuthLoginView, AuthCallbackView, UserLogoutView

app_name = 'oauth'

urlpatterns = [
    path('student/', StudentAuthLoginView.as_view(), name='student'),
    path('teacher/', TeacherAuthLoginView.as_view(), name='teacher'),
    path('callback/', AuthCallbackView.as_view(), name='callback'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
]
