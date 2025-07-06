from django import forms
from .models import PDFResource

class PDFUploadForm(forms.ModelForm):
    class Meta:
        model = PDFResource
        fields = ['title', 'description', 'file']
