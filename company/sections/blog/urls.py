from django.urls import path
from .views import (
    PostListView, 
    #PostDetailView, 
    PostCreateView,
    PostUpdateView,
    PostDeleteView,
    # UserPostListView
)
from . import views


urlpatterns = [
    path('new/', PostCreateView.as_view(), name="post-create"),
    path('blogs/', PostListView.as_view(), name="blog-home"),
    path('detail/<slug:slug>/', views.post_detail, name="blog-detail"),
    path('like/<slug:slug>/', views.toggle_like, name='toggle_like'),
    path('update/<slug:slug>/', PostUpdateView.as_view(), name="blog-update"),
    path('post/<slug:slug>/delete/', PostDeleteView.as_view(), name="blog-delete"),
]