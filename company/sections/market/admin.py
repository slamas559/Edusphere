from django.contrib import admin
from .models import Product, Category, Review, Wishlist

admin.site.register(Product)

admin.site.register(Review)
admin.site.register(Wishlist)

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}  # Auto-generate slug
    list_display = ("name", "parent")

admin.site.register(Category, CategoryAdmin)
