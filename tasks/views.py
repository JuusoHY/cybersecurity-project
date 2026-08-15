from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from .forms import TaskForm
from .models import Task


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()

    return render(request, 'registration/signup.html', {'form': form})


@login_required
def home_view(request):
    query = request.GET.get('q', '')

    if query:
        # FLAW 1: A1:2017 Injection
        # User input is inserted directly into an SQL query.
        sql = (
            "SELECT * FROM tasks_task "
            "WHERE owner_id = %s AND title LIKE '%%%s%%'"
            % (request.user.id, query)
        )
        tasks = Task.objects.raw(sql)
    else:
        tasks = Task.objects.filter(
            owner=request.user
        ).order_by('-created_at')

    return render(
        request,
        'tasks/index.html',
        {
            'tasks': tasks,
            'query': query,
        }
    )


# FIX: Replace the vulnerable home_view function above with the
# following fixed version, which uses the Django ORM to parameterize
# user input safely.
#
# @login_required
# def home_view(request):
#     query = request.GET.get('q', '')
#
#     if query:
#         tasks = Task.objects.filter(
#             owner=request.user,
#             title__icontains=query
#         ).order_by('-created_at')
#     else:
#         tasks = Task.objects.filter(
#             owner=request.user
#         ).order_by('-created_at')
#
#     return render(
#         request,
#         'tasks/index.html',
#         {
#             'tasks': tasks,
#             'query': query,
#         }
#     )


@login_required
def add_task_view(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)

        if form.is_valid():
            task = form.save(commit=False)
            task.owner = request.user
            task.save()

    return redirect('home')


@login_required
@require_POST
@csrf_exempt
def delete_task_view(request, task_id):
    # FLAW 5: CSRF (Cross-Site Request Forgery)
    # CSRF protection is disabled, allowing an attacker to trick a
    # logged-in user into deleting tasks without their consent.
    task = get_object_or_404(
        Task,
        pk=task_id,
        owner=request.user
    )
    task.delete()

    return redirect('home')


# FIX: Replace the vulnerable delete_task_view function above with the
# following fixed version, which removes @csrf_exempt. CSRF protection
# is enabled by default, and the form already includes {% csrf_token %}.
#
# @login_required
# @require_POST
# def delete_task_view(request, task_id):
#     task = get_object_or_404(
#         Task,
#         pk=task_id,
#         owner=request.user
#     )
#     task.delete()
#
#     return redirect('home')


@login_required
def task_detail_view(request, task_id):
    # FLAW 3: A5:2017 Broken Access Control
    # The task is fetched by ID only, without checking ownership.
    task = get_object_or_404(Task, pk=task_id)

    return render(request, 'tasks/task_detail.html', {'task': task})


# FIX: Replace the vulnerable task_detail_view function above with the
# following fixed version, which restricts the lookup to tasks owned
# by the current user.
#
# @login_required
# def task_detail_view(request, task_id):
#     task = get_object_or_404(Task, pk=task_id, owner=request.user)
#
#     return render(request, 'tasks/task_detail.html', {'task': task})


@login_required
def change_password_view(request):
    if request.method == 'POST':
        target_username = request.POST.get('username', '')
        current_password = request.POST.get('current_password', '')
        new_password = request.POST.get('new_password', '')

        # FLAW 2: A2:2017 Broken Authentication
        # The current password is never verified, and any logged-in user
        # can change any other user's password by supplying their username.
        target_user = User.objects.get(username=target_username)

        try:
            validate_password(new_password, user=target_user)
        except ValidationError as e:
            return render(request, 'tasks/change_password.html', {
                'error': ' '.join(e.messages)
            })

        target_user.set_password(new_password)
        target_user.save()

        # If the target user is the current user, keep them logged in.
        if target_user == request.user:
            update_session_auth_hash(request, request.user)

        return redirect('home')

    return render(request, 'tasks/change_password.html')


# FIX: Replace the vulnerable change_password_view function above with
# the following fixed version, which verifies the current password,
# prevents changing another user's password, and validates the new
# password strength.
#
# @login_required
# def change_password_view(request):
#     if request.method == 'POST':
#         target_username = request.POST.get('username', '')
#         current_password = request.POST.get('current_password', '')
#         new_password = request.POST.get('new_password', '')
#
#         if target_username != request.user.username:
#             return render(request, 'tasks/change_password.html', {
#                 'error': 'You can only change your own password.'
#             })
#
#         if not request.user.check_password(current_password):
#             return render(request, 'tasks/change_password.html', {
#                 'error': 'Current password is incorrect.'
#             })
#
#         try:
#             validate_password(new_password, user=request.user)
#         except ValidationError as e:
#             return render(request, 'tasks/change_password.html', {
#                 'error': ' '.join(e.messages)
#             })
#
#         request.user.set_password(new_password)
#         request.user.save()
#         update_session_auth_hash(request, request.user)
#
#         return redirect('home')
#
#     return render(request, 'tasks/change_password.html')