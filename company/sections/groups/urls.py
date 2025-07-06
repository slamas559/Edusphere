from django.urls import path
from . import views
from .views import GroupView, QuestionDeleteView

urlpatterns = [
    path('home', GroupView.as_view(), name="group-home"),
    path('details/<slug:slug>/', views.about_group, name="group-detail"),
    path('create/', views.GroupCreateView.as_view(), name="group-create"),
    path('join/<slug:slug>/', views.group_join, name="group-join"),
    path('accept/<str:user>/<slug:slug>/', views.accept_request, name="group-accept"),
    path('leave/<slug:slug>/', views.leave_group, name="group-leave"),
    path('question/<slug:slug>/add/', views.add_group_question, name="group-add-question"),
    path('question/<int:pk>/delete/', QuestionDeleteView.as_view(), name="group-delete-question"),
    path('question/submit/<int:question_id>/', views.submit_answer, name='submit-answer'),
]