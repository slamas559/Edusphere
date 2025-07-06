from django import forms
from .models import Product, Review

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["title", "description", "location", "price", "category", "image"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3, "class": "form-input"}),
            "title": forms.TextInput(attrs={"class": "form-input"}),
            "price": forms.NumberInput(attrs={"class": "form-input"}),
            "category": forms.Select(attrs={"class": "form-input"}),
            "image": forms.FileInput(attrs={"class": "form-input"}),
        }

class Filter(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["category"]


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]
