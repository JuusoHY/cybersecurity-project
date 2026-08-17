from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

# Part of FLAW 5: A3:2017 Sensitive Data Exposure
# Also, notice that code and fixes for FLAW 5 are in in line 30 and 195
# of this views.py and in line 15 of models.py too
from .models import Task, UserSecret
# FIX for flaw 5: When UserSecret is removed, change the import above to:
# from .models import Task

from .forms import TaskForm


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()

            # Part of FLAW 5: A3:2017 Sensitive Data Exposure
            # The user's plaintext password is stored in the database.
            # Also, notice that code and fixes for FLAW 5 are in in line 10 and 195
            # of this views.py and in line 15 of models.py too
            #
            UserSecret.objects.create(
                user=user,
                plaintext_password=form.cleaned_data['password1']
            )

            # FIX: Remove the plaintext password storage above.
            # Django's User model already stores a hashed password
            # securely. No replacement code is needed.


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
def delete_task_view(request, task_id):
    task = get_object_or_404(
        Task,
        pk=task_id,
        owner=request.user
    )
    task.delete()

    return redirect('home')




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

        # =========================================================
        # FLAW 2: A2:2017 Broken Authentication
        # ---------------------------------------------------------
        # Vulnerability: The current password is never verified, and any
        # logged-in user can change another user's password by supplying
        # their username.
        # ---------------------------------------------------------
        target_user = User.objects.get(username=target_username)

        # FIX for FLAW 2:
        # Replace the target_user lookup above with the following checks
        # before changing the password:
        #
        # if target_username != request.user.username:
        #     return render(request, 'tasks/change_password.html', {
        #         'error': 'You can only change your own password.'
        #     })
        #
        # if not request.user.check_password(current_password):
        #     return render(request, 'tasks/change_password.html', {
        #         'error': 'Current password is incorrect.'
        #     })


        try:
            validate_password(new_password, user=target_user)
        except ValidationError as e:
            return render(request, 'tasks/change_password.html', {
                'error': ' '.join(e.messages)
            })

        # =========================================================
        # Part of FLAW 5: A3:2017 Sensitive Data Exposure
        # ---------------------------------------------------------
        # Vulnerability: The new password is stored in plain text in
        # the UserSecret model.
        # Also, notice that code and fixes for FLAW 5 are in in line 10 and 30
        # of this views.py and in line 15 of models.py too
        # ---------------------------------------------------------

        secret, created = UserSecret.objects.get_or_create(user=target_user)
        secret.plaintext_password = new_password
        secret.save()

        # FIX for FLAW 5:
        # Remove the three lines above (get_or_create, assignment, save)
        # because they store the password in plain text.



        target_user.set_password(new_password)
        target_user.save()


        if target_user == request.user:
            update_session_auth_hash(request, request.user)

        return redirect('home')

    return render(request, 'tasks/change_password.html')