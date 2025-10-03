from django.contrib import admin
from .models import VideoRoom, RoomParticipant

@admin.register(VideoRoom)
class VideoRoomAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'room_id', 'start_time', 'is_active', 'max_participants', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'owner__username', 'room_id')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

@admin.register(RoomParticipant)
class RoomParticipantAdmin(admin.ModelAdmin):
    list_display = ('room', 'user', 'is_host', 'joined_at')
    list_filter = ('is_host', 'joined_at')
    search_fields = ('room__title', 'user__username')
    ordering = ('-joined_at',)
    readonly_fields = ('joined_at',)
