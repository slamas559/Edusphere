from django.db import models
from django.contrib.auth.models import User
from pdf2image import convert_from_path, convert_from_bytes
import PyPDF2
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image
import os
from cloudinary_storage.storage import RawMediaCloudinaryStorage



# Create your models here.

class PDFResource(models.Model):
    title = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='pdfs/', blank=True, storage=RawMediaCloudinaryStorage())
    cover_image = models.ImageField(upload_to='pdf_thumbnails/', blank=True, null=True)
    page_count = models.IntegerField(null=True, blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    author = models.CharField(max_length=255, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.file:
            # Open file from storage (works with Cloudinary too)
            self.file.open()
            file_bytes = self.file.read()

            # Check for poppler_path safely
            poppler_path = os.getenv("POPPLER_PATH", None)  # e.g., you can set in .env if needed
            convert_kwargs = {"first_page": 1, "last_page": 1}
            if poppler_path and os.path.exists(poppler_path):
                convert_kwargs["poppler_path"] = poppler_path

            # Generate cover image if not already created
            if not self.cover_image:
                try:
                    images = convert_from_bytes(file_bytes, **convert_kwargs)
                    if images:
                        image = images[0]
                        thumb_io = BytesIO()
                        image.save(thumb_io, format='JPEG')
                        image_name = f'{self.pk}_preview.jpg'
                        self.cover_image.save(
                            image_name,
                            ContentFile(thumb_io.getvalue()),
                            save=False
                        )
                except Exception as e:
                    # Optional: log or print the error so you know what went wrong
                    print(f"Error generating cover image: {e}")

            # Count pages if not already set
            if not self.page_count:
                try:
                    reader = PyPDF2.PdfReader(BytesIO(file_bytes))
                    self.page_count = len(reader.pages)
                except Exception as e:
                    print(f"Error counting pages: {e}")

            # Extract author if not already set
            if not self.author:
                try:
                    reader = PyPDF2.PdfReader(BytesIO(file_bytes))
                    metadata = reader.metadata
                    self.author = metadata.author if metadata and metadata.author else "Unknown"
                except Exception as e:
                    print(f"Error extracting author: {e}")

            # Save updates
            super().save(update_fields=['cover_image', 'page_count', 'author'])

