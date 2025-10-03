# models.py
from django.db import models
from apps.account.models import User
import uuid

class VideoRoom(models.Model):
    room_id = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_rooms')
    subject_title = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_time = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    max_participants = models.IntegerField(default=50)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.owner.username}"

class RoomParticipant(models.Model):
    room = models.ForeignKey(VideoRoom, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    is_host = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['room', 'user']
