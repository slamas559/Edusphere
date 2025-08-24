from django.shortcuts import render, redirect, get_object_or_404
from .models import PDFResource
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.db.models import Count, Q
from .forms import PDFUploadForm
from django.contrib.auth import get_user_model

# Use this to get the user model
User = get_user_model()

class PDFListView(ListView):
    model = PDFResource
    template_name = 'archive/pdf_list.html'
    context_object_name = 'pdfs'
    ordering = ['-uploaded_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(Q(title__icontains=query)|Q(uploaded_by__username__icontains=query)).distinct()
        return queryset

def pdf_upload(request):
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            pdf = form.save(commit=False)
            pdf.uploaded_by = request.user
            pdf.save()
            return redirect('archive')
    else:
        form = PDFUploadForm()
    return render(request, 'archive/pdf_upload.html', {'form': form})

def pdf_detail(request, pk):
    pdf = get_object_or_404(PDFResource, pk=pk)
    return render(request, 'archive/pdf_details.html', {'pdf': pdf})

