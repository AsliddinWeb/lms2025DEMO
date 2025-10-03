# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from .models import VideoRoom, RoomParticipant

ZEGO_APP_ID = 1993402830
ZEGO_SERVER_SECRET = "c98f06c4413a2fa9a976c62c0022c963"

@login_required
def create_room(request):
    """Yangi room yaratish"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        max_participants = int(request.POST.get('max_participants', 50))
        
        room = VideoRoom.objects.create(
            owner=request.user,
            title=title,
            description=description,
            max_participants=max_participants
        )
        
        # Owner'ni host sifatida qo'shamiz
        RoomParticipant.objects.create(
            room=room,
            user=request.user,
            is_host=True
        )
        
        messages.success(request, 'Room muvaffaqiyatli yaratildi!')
        return redirect('room_detail', room_id=room.room_id)
    
    return render(request, 'chat/create_room.html')

@login_required(login_url=reverse_lazy('oauth:student'))
def room_detail(request, room_id):
    """Room sahifasi"""
    room = get_object_or_404(VideoRoom, room_id=room_id, is_active=True)
    
    # Foydalanuvchi owner yoki ishtirokchi ekanligini tekshirish
    is_owner = room.owner == request.user
    participant, created = RoomParticipant.objects.get_or_create(
        room=room,
        user=request.user,
        defaults={'is_host': is_owner}
    )
    
    # Ishtirokchilar sonini tekshirish
    participant_count = room.participants.count()
    if participant_count > room.max_participants and not is_owner:
        messages.error(request, 'Room to\'lgan!')
        return redirect('room_list')
    
    context = {
        'room': room,
        'is_owner': is_owner,
        'is_host': participant.is_host,
        'app_id': ZEGO_APP_ID,
        'server_secret': ZEGO_SERVER_SECRET,
        'user_id': str(request.user.id),
        'username': request.user.username,
    }
    
    return render(request, 'chat/room.html', context)

@login_required
def my_rooms(request):
    """Mening roomlarim"""
    owned_rooms = VideoRoom.objects.filter(owner=request.user, is_active=True)
    joined_rooms = VideoRoom.objects.filter(
        participants__user=request.user,
        is_active=True
    ).exclude(owner=request.user)
    
    context = {
        'owned_rooms': owned_rooms,
        'joined_rooms': joined_rooms,
    }
    return render(request, 'chat/my_rooms.html', context)

@login_required
def close_room(request, room_id):
    """Roomni yopish (faqat owner)"""
    room = get_object_or_404(VideoRoom, room_id=room_id, owner=request.user)
    room.is_active = False
    room.save()
    messages.success(request, 'Room yopildi!')
    return redirect('dashboard:home')

@login_required
def kick_participant(request, room_id, user_id):
    """Ishtirokchini chiqarib yuborish (faqat owner)"""
    room = get_object_or_404(VideoRoom, room_id=room_id, owner=request.user)
    participant = get_object_or_404(RoomParticipant, room=room, user_id=user_id)
    
    if participant.user != room.owner:
        participant.delete()
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Owner\'ni chiqarib bo\'lmaydi'})
