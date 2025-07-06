from django.urls import path
from .views import ProductDetailView, ProductCreateView, ProductUpdateView, ProductListView

urlpatterns = [
    path("", ProductListView.as_view(), name="market-home"),
    path("product/<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
    path("product/new/", ProductCreateView.as_view(), name="product-create"),
    path("product/<int:pk>/edit/", ProductUpdateView.as_view(), name="product-update"),
]
