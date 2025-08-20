from django.shortcuts import render
from .models import Group, MemberScore, Question, AnswerOption, MemberAnswer, Post, Comment
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_POST
from sections.notifications.views import send_notification
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from .forms import GroupPostForm, CommentForm

# Create your views here.

class GroupView(ListView):
    model = Group
    template_name = "groups/group_home.html"  # Template path
    context_object_name = "groups"
    # ordering = ["-created_at"]  # Show newest first

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("q")

        if query:
            queryset = queryset.filter(Q(name__icontains=query)|Q(bio__icontains=query)).distinct()
        return queryset

def about_group(request, slug):
    group = get_object_or_404(Group, slug=slug)
    # questions = Question.objects.filter(group=group).prefetch_related('options')
    questions = group.questions.prefetch_related('options').all()
    members = group.members.all()
    posts = group.posts.all()

    answered_question_ids = MemberAnswer.objects.filter(
        user=request.user, question__in=questions
    ).values_list('question_id', flat=True)

    
    rankings = (
        User.objects
        .filter(id__in=members.values_list('id', flat=True))
        .annotate(score=Count('membersanswer', filter=Q(membersanswer__correct=True)))
        .order_by('-score', 'username')  # Highest scores first
    )

    context = {
        "group": group,
        "questions": questions,
        'answered_question_ids': list(answered_question_ids),
        "rankings":rankings,
        "posts": posts,
    }
    return render(request, "groups/group_details.html", context=context)

@login_required
@require_POST
def submit_answer(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    selected_option_id = request.POST.get('option')

    if not selected_option_id:
        return JsonResponse({'error': 'No option selected'}, status=400)

    selected_option = get_object_or_404(AnswerOption, id=selected_option_id, question=question)
    is_correct = selected_option.is_correct

    already_answered = MemberAnswer.objects.filter(
        user=request.user, question=question
    ).exists()

    if already_answered:
        return JsonResponse({'already_answered': True}, status=200)

    # Save or update the user's answer
    MemberAnswer.objects.update_or_create(
        user=request.user,
        question=question,
        defaults={'selected_option': selected_option,
                  'correct': is_correct}
    )

    correct_option = question.options.filter(is_correct=True).first()

    if is_correct:
        messages.success(request, "You earn a point 🎉🎊")
    else:
        messages.error(request, "Wrong answer 😢!")

    return JsonResponse(
        {'correct': is_correct,
        'correct_option_id': correct_option.id,
        'correct_option_text': correct_option.text,
        'message': "You earn a point 🎉🎊" if is_correct else "Wrong answer 😢!"
        }, status=200)
        
class GroupCreateView(LoginRequiredMixin, CreateView):
    model = Group
    fields = ["name", "bio", "profile_picture"]  
    template_name = "groups/group_form.html"

    def form_valid(self, form):
        form.instance.creator = self.request.user  # Set the creator as the logged-in user        
        response =  super().form_valid(form)
        
        return response

class GroupUpdateView(LoginRequiredMixin, UpdateView):
    model = Group
    fields = ["name", "bio", "profile_picture"]  
    template_name = "groups/group_form.html"

    def get_queryset(self):
        return Group.objects.filter(creator=self.request.user)  # Restrict updates to product owner

class QuestionDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Question
    success_url = "/"

    def test_func(self):
        question = self.get_object()
        if self.request.user == question.created_by:
            return True
        return False

def group_join(request, slug):
    group = get_object_or_404(Group, slug=slug)
    user = request.user
    admins = group.admin.all()

    messages.info(request, "You request as been sent ✈ you will be notified shortly")
    for admin in admins:
        send_notification(admin, user, f"{user.username} requested to join {group.name}", "request", group)
    
    return redirect('group-detail', slug)  # Redirect to the previous page

def accept_request(request, user, slug):
    sender = get_object_or_404(User, username=user)
    group = get_object_or_404(Group, slug=slug)
    if sender not in group.members.all():
        messages.info(request, f"{sender} is now a member of {group.name}")
        group.members.add(sender)
    else:
        messages.info(request, f"{sender} is already a member!")

    return redirect('notification-inbox')


def leave_group(request, slug):
    group = get_object_or_404(Group, slug=slug)
    user = request.user
    if user in group.members.all():
        messages.info(request, f"You have been removed from {group.name}")
        group.members.remove(user)

    return redirect('group-detail', slug)  # Redirect to the previous page

def group_leaderboard(request, slug):
    group = get_object_or_404(Group, slug=slug)
    scores = MemberScore.objects.filter(group=group).select_related('user').order_by('-points')
    return render(request, "groups/leaderboard.html", {"group": group, "scores": scores})

@login_required
def add_group_question(request, slug):
    group = get_object_or_404(Group, slug=slug)

    if request.user not in group.admin.all():
        return redirect("not_authorized")

    if request.method == "POST":
        question_text = request.POST.get("question")
        correct_index = request.POST.get("correct_option")

        if question_text and correct_index:
            question = Question.objects.create(
                group=group,
                text=question_text,
                created_by=request.user
            )

            for i in range(1, 5):
                option_text = request.POST.get(f"option_{i}")
                if option_text:
                    AnswerOption.objects.create(
                        question=question,
                        text=option_text,
                        is_correct=(str(i) == correct_index)
                    )

            return redirect("group-detail", group.slug)

    return render(request, "groups/group_question_form.html", {"group": group})

@login_required
def create_view(request, slug):
    group = get_object_or_404(Group, slug=slug)
    form = GroupPostForm()

    if request.user not in group.members.all():
        return redirect("not_authorized")
    
    if request.method == "POST":
        form = GroupPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.group = group
            post.save()
            return redirect('group-detail', slug=slug)
        else:
            form = GroupPostForm()
    return render(request, 'groups/post_form.html', { 'form': form })

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    comments = post.group_comments.filter(post=post, parent__isnull=True).order_by('-created_at')
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
            return redirect('post-detail', slug=slug)

    context = {
        "post": post,
        'comments': comments,
        'form': form
    }
    return render(request, "groups/post_details.html", context=context)

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
    # success_url = f"/group/details/",
    success_url = "/group/home"

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
