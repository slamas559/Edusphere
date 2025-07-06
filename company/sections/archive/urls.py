from django.urls import path
from . import views
from .views import PDFListView

urlpatterns = [
    path('', PDFListView.as_view(), name='archive'),
    path('upload/', views.pdf_upload, name='pdf-upload'),
    path('<int:pk>/', views.pdf_detail, name='pdf-detail'),
]
