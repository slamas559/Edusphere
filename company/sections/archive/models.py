from django.db import models
from django.contrib.auth.models import User
from pdf2image import convert_from_path
import PyPDF2
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image


# Create your models here.

class PDFResource(models.Model):
    title = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='pdfs/')
    cover_image = models.ImageField(upload_to='pdf_thumbnails/', blank=True, null=True)
    page_count = models.IntegerField(null=True, blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    author = models.CharField(max_length=255, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Generate preview if not already created
        if self.file and not self.cover_image:
            images = convert_from_path(self.file.path, first_page=1, last_page=1)
            if images:
                image = images[0]
                thumb_io = BytesIO()
                image.save(thumb_io, format='JPEG')
                image_name = f'{self.pk}_preview.jpg'
                self.cover_image.save(image_name, ContentFile(thumb_io.getvalue()), save=False)
                super().save(update_fields=['cover_image'])
        if self.file and not self.page_count:
            self.file.seek(0)
            reader = PyPDF2.PdfReader(self.file)
            self.page_count = len(reader.pages)
        if self.file and not self.author:
            self.file.seek(0)
            reader = PyPDF2.PdfReader(self.file)
            metadata = reader.metadata
            self.author = metadata.author if metadata.author else "Unknown"
        super().save(*args, **kwargs)

    # def __str__(self):
    #     return self.title
