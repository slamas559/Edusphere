from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import Profile, CustomUser
from sections.blog.models import Post
from sections.market.models import Product
from .forms import CustomUserCreationForm, UserUpdateForm, ProfileUpdateForm, CustomAuthenticationForm
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.contrib.auth import login, authenticate

class LoginView(auth_views.LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'registration/login.html'
    
    def get_success_url(self):
        return reverse_lazy('home')

# Create your views here.
def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # FIX: Authenticate the user before logging in to handle multiple backends
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            authenticated_user = authenticate(request, username=username, password=password)
            
            if authenticated_user:
                login(request, authenticated_user)
            else:
                # Fallback: Set backend manually if authentication fails
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)
            
            messages.success(request, f"✔ Your account has been created! Welcome to EduSphere.")
            return redirect("home")
        else:
            # Check if email already exists
            if 'email' in form.errors:
                messages.error(request, f"Sorry 😢 This email is already registered.")
            else:
                messages.error(request, f"Please correct the errors below.")
    else:
        form = CustomUserCreationForm()
    return render(request, "users/register.html", {"form": form})

@login_required
def profile(request, slug):
    profile_obj = get_object_or_404(Profile, slug=slug)
    posts = Post.objects.filter(author=profile_obj.user).order_by("-date_posted")[:4]
    products = Product.objects.filter(seller=profile_obj.user)[:3]
    context = {
        "owner": profile_obj,
        "posts": posts,
        "products": products,
    }
    return render(request, "users/profile.html", context=context)

@login_required
def edit_profile(request):
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                    request.FILES, 
                                    instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f"✔ Your account has been updated!")
            return redirect("profile", request.user.profile.slug)

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        "u_form": u_form,
        "p_form": p_form
    }
    return render(request, "users/profile_edit.html", context=context)


def user_logout(request):
    logout(request)
    return render(request, "users/logout.html")