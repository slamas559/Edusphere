from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import User
from .models import Profile
from sections.blog.models import Post
from sections.market.models import Product
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm



# Create your views here.
def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            username = form.cleaned_data.get("username")
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, f"✔ Your account as has been now been created! You are now able to login")
            return redirect("login")
        else:
            messages.error(request, f"Sorry 😢 Username already exist choose another")
    else:
        form = UserRegisterForm()
    return render(request, "users/register.html", {"form":form})


@login_required
def profile(request, slug):
    user = get_object_or_404(Profile, slug=slug)
    posts = Post.objects.filter(author=user.user).order_by("-date_posted")[:4]
    products = Product.objects.filter(seller=user.user)[:3]
    context = {
        "owner":user,
        "posts":posts,
        "products":products,
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
        "u_form" : u_form,
        "p_form" : p_form
    }
    return render(request, "users/profile_edit.html", context=context)


def user_logout(request):
    logout(request)
    return render(request, "users/logout.html")


