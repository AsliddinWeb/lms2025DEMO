from django.shortcuts import render, redirect, get_object_or_404

from .utils import get_student_subjects, get_my_info, get_subject_detail, get_subject_resources

from apps.chat.models import VideoRoom, RoomParticipant

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy

ZEGO_APP_ID = 1993402830
ZEGO_SERVER_SECRET = "c98f06c4413a2fa9a976c62c0022c963"


def home_dashboard(request):
    if request.user.role == 'teacher':
        return render(request, 'teacher/home.html')
    else:
        return render(request, 'dashboard/home.html')


# Subjects
def subjects_list(request):
    subjects_data = get_student_subjects(request).get('data')

    my_data = get_my_info(request).get('data')
    my_semester = my_data.get('semester').get('code')

    # Transform qilish
    subjects = []

    for s in subjects_data:
        if s["_semester"] == my_semester:
            subjects.append({
                "id": s["subject"]["id"],
                "name": s["subject"]["name"],
                "code": s["subject"]["code"],
                "subject_type": s["subjectType"]["name"],
                "semester": my_data.get('semester').get('name'),
                "total_acload": s["total_acload"],
                "credit": s["credit"],
            })


    context = {
        "subjects": subjects,
        "semester": my_data.get('semester').get('name'),
    }
    return render(request, 'dashboard/subjects/list.html', context)


# Subject Detail
def subject_detail(request, subject_id):
    

    my_data = get_my_info(request).get('data')
    my_semester = my_data.get('semester').get('code')

    subject_data = get_subject_detail(request=request, semester=my_semester, subject=subject_id).get('data')
    subject_resources = get_subject_resources(request=request, semester=my_semester, subject=subject_id).get('data')

    context = {
        "subject": subject_data,
        "semester": my_data.get('semester').get('name'),
        "subject_resources": subject_resources,
    }
    return render(request, 'dashboard/subjects/detail.html', context)


def room_list(request):
    if request.user.role == 'student':
        video_rooms = VideoRoom.objects.filter(is_active=True)

        ctx = {
            'video_rooms': video_rooms
        }
        return render(request, 'dashboard/chat/list.html', ctx)
    else:
        video_rooms = VideoRoom.objects.filter(is_active=True, owner=request.user)
        ctx = {
            'video_rooms': video_rooms
        }
        return render(request, 'teacher/chat/list.html', ctx)
    

@login_required
def create_room(request):
    if request.user.role != 'teacher':
        messages.error(request, "Faqat o'qituvchilar jonli dars yaratishi mumkin!")
        return redirect('dashboard:home')

    if request.method == 'POST':
        subject_title = request.POST.get('subject_title')
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        start_time = request.POST.get('start_time')
        max_participants = int(request.POST.get('max_participants', 50))
        is_active = True if request.POST.get('is_active') == 'on' else False

        # Room yaratish
        room = VideoRoom.objects.create(
            owner=request.user,
            subject_title=subject_title,
            title=title,
            description=description,
            start_time=start_time,
            max_participants=max_participants,
            is_active=is_active,
        )

        # Owner'ni host sifatida qo‘shish
        RoomParticipant.objects.create(
            room=room,
            user=request.user,
            is_host=True
        )

        messages.success(request, "Jonli dars muvaffaqiyatli yaratildi!")
        return redirect('dashboard:room_detail', room_id=room.room_id)

    return render(request, 'teacher/chat/create.html')


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

    return render(request, 'teacher/chat/room.html', context)