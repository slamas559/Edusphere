# audio/forms.py
from django import forms
from .models import AudioRoom
from django.contrib.auth.models import User

class AudioRoomForm(forms.ModelForm):
    allowed_users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = AudioRoom
        fields = ['name', 'is_group', 'allowed_users']
