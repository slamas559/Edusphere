from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Product, Review, Category
from django.db.models import Q
from .forms import ProductForm, ReviewForm, Filter
from django.contrib.auth import get_user_model

# Use this to get the user model
User = get_user_model()

# List all products
class ProductListView(ListView):
    model = Product
    template_name = "market/product_list.html"  # Template path
    context_object_name = "products"
    ordering = ["-created_at"]  # Show newest first

    def get_queryset(self):
        queryset = super().get_queryset().select_related('category')
        query = self.request.GET.get("q")
        category_slug = self.request.GET.get("category")

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            ).distinct()

        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass available categories to the template
        context["categories"] = Category.objects.all()
        context["selected_category"] = self.request.GET.get("category", "")
        return context



def product_list(request):
    products = Product.objects.all().order_by("-created_at")
    filters = Filter()
    info = ""
    seen = False

    # initializing a search
    if request.method == 'GET':
        searched = request.GET.get('search')
        if searched:
            for product in products:
                searched = searched.lower()
                product_name = product.title.lower()
                if searched in product_name:
                    products = Product.objects.filter(title=product.title).order_by('-created_at')
                    seen = True
                    print(searched, product.title)
                if not seen:
                    print("wrong")
                    products = {}
                    info = f"No Result for {searched}"

    if request.method == "POST":
        form = Filter(request.POST)
        form.save(commit=False)
        form = form.cleaned_data.get("category")
        print(form)

    return render(request, "market/product_list.html", {"products": products, "info": info, "filter":filters})

# View product details
class ProductDetailView(DetailView, CreateView):
    model = Product
    form_class = ReviewForm
    template_name = "market/product_details.html"
    context_object_name = "product"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get related products from the same category (excluding the current product)
        context["related_products"] = Product.objects.filter(
            category=self.object.category
        ).exclude(id=self.object.id)[:3]
        context["reviews"] = Review.objects.filter(
            seller = self.object.seller
        ).order_by("-created_at")[:3]  # Get the latest 2 reviews for the seller

        return context
    
    def form_valid(self, form):
        product = self.get_object()
        form.instance.buyer = self.request.user
        form.instance.seller = product.seller
        form.instance.product = product
        
        return super().form_valid(form)

# Create a new product (only logged-in users)
class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm  # Use a form for validation
    template_name = "market/product_form.html"

    def form_valid(self, form):
        form.instance.seller = self.request.user  # Set the seller as the logged-in user
        return super().form_valid(form)

# Update a product (only seller can update)
class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "market/product_form.html"

    def get_queryset(self):
        return Product.objects.filter(seller=self.request.user)  # Restrict updates to product owner
