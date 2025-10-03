# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_room, name='create_room'),
    path('room/<str:room_id>/', views.room_detail, name='room_detail'),
    path('my-rooms/', views.my_rooms, name='my_rooms'),
    path('room/<str:room_id>/close/', views.close_room, name='close_room'),
    path('room/<str:room_id>/kick/<int:user_id>/', views.kick_participant, name='kick_participant'),
]