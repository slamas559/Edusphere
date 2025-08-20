from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
import random
from django.urls import reverse, reverse_lazy
from cloudinary.models import CloudinaryField
from cloudinary.utils import cloudinary_url

# Categories (e.g., Books, Electronics, Notes, etc.)
class Category(models.Model):
    name = models.CharField(max_length=255)  # Unique category name
    slug = models.SlugField(unique=True, default="")  # URL-friendly name
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories'
    )  # Allows subcategories

    class Meta:
        ordering = ['name']  # Order categories alphabetically

    def __str__(self):
        return self.name
    
# Product Listings
class Product(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = CloudinaryField("image", blank=True, null=True)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)  # Seller (User)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="products")
    location = models.CharField(max_length=255, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    is_sold = models.BooleanField(default=False)
    slug = models.SlugField(default="", null=False, unique=True)

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.id = random.randint(100000000000, 999999999999)  # 12-digit random number
        if not self.slug:
            self.slug = f"{self.id}-{slugify(self.title)}--{self.seller.username}"  # Example: 123456789012-my-title
        return super().save(*args, **kwargs)

    def get_resized_image(self, width=400, height=400, crop="fill"):
        if not self.image:
            return None
        url, options = cloudinary_url(
            self.image.public_id,
            width=width,
            height=height,
            crop=crop
        )
        return url
    
    def get_absolute_url(self):
        return reverse("product-detail", kwargs={"pk":self.pk})

# User Reviews for Sellers
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product")
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="given_reviews")
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_reviews")
    rating = models.PositiveIntegerField(default=5)  # Rating (1-5)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.buyer.username} → {self.seller.username} ({self.rating} Stars)"

    def get_absolute_url(self):
        return reverse("product-detail", kwargs={"pk":self.product.pk})
    
# Wishlist for Users
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} saved {self.product.title}"
