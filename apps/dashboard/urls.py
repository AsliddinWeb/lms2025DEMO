from . import views
from django.urls import path

app_name = 'dashboard'

urlpatterns = [
    # Dashboard
    path('', views.home_dashboard, name='home'),

    # Subjects
    path('subjects/', views.subjects_list, name='subjects_list'),
    path('subjects/<int:subject_id>/', views.subject_detail, name='subject_detail'),

    # Chat
    path('lessons/', views.room_list, name='lessons'),
    path('lessons/create/', views.create_room, name='create_lesson'),
    path('lessons/detail/<str:room_id>/', views.room_detail, name='room_detail'),
]
