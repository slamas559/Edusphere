from django.shortcuts import render
# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
# from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.views.generic import (
    ListView, 
    DetailView, 
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView)
from .models import Post, Comment
from .forms import CommentForm
from django.utils.text import slugify
from sections.notifications.views import send_notification
from django.contrib.auth import get_user_model

# Use this to get the user model
User = get_user_model()

# Create your views here.


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ["title", "content", "image"]  

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
class PostListView(ListView):
    model = Post
    template_name = "blog/blogs.html"
    context_object_name = "posts"
    ordering = ["-date_posted"]
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(content__icontains=query)
            ).distinct()
        return queryset


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    comments = post.comments.filter(post=post, parent__isnull=True).order_by('-created_at')
    form = CommentForm()

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            parent_id = request.POST.get('parent_id')
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            if parent_id:
                parent_comment = Comment.objects.get(id=parent_id)
                comment.parent = parent_comment
            comment.save()
            return redirect('blog-detail', slug=slug)

    context = {
        "post": post,
        'comments': comments,
        'form': form
    }
    return render(request, "blog/post_details.html", context=context)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ["title", "content", "image"]

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False
    
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = "/"

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

@require_POST
@login_required
def toggle_like(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        send_notification(post.author, request.user, f"{request.user} likes your post '{post.title}'", "like")
        liked = True
    return JsonResponse({'liked': liked, 'like_count': post.total_likes()})
