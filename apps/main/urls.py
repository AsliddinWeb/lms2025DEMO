from django.urls import path

from .views import home_page, room_page

app_name = 'main'

urlpatterns = [
    # Home Landing Page
    path('', home_page, name='home_page'),
    path('room/', room_page, name='room_page'),
]
