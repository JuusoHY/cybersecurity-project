from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

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

        # FIX:
        # Use Django ORM so that user input is safely parameterized.
        # tasks = Task.objects.filter(
        #     owner=request.user,
        #     title__icontains=query
        # ).order_by('-created_at')
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