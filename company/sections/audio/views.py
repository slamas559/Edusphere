from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from .models import AudioRoom
from .forms import AudioRoomForm
from django.contrib.auth.decorators import login_required


@login_required
def group_room_view(request, room_name):
    room = get_object_or_404(AudioRoom, name=room_name)
    return render(request, 'audio/group_room.html', {'room_name': room})


@login_required
def create_room(request):
    if request.method == 'POST':
        form = AudioRoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.created_by = request.user
            room.save()
            form.save_m2m()
            return redirect('group-audio-room', room_name=room.name)
    else:
        form = AudioRoomForm()
    return render(request, 'audio/create_room.html', {'form': form})

@login_required
def join_room(request, room_name):
    room = get_object_or_404(AudioRoom, name=room_name)
    
    # Optional: add access control here
    if room.is_group:
        return redirect('group-audio-room', room_name=room.name)

    # Maybe log the invite or check access permissions

    return redirect('group-audio-room', room_name=room.name)