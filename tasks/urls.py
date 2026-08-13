from django.urls import path

from .views import (
    add_task_view,
    change_password_view,
    delete_task_view,
    home_view,
    signup_view,
)


urlpatterns = [
    path('', home_view, name='home'),
    path('signup/', signup_view, name='signup'),
    path('tasks/add/', add_task_view, name='add_task'),
    path(
        'tasks/<int:task_id>/delete/',
        delete_task_view,
        name='delete_task'
    ),
    path(
        'password/change/',
        change_password_view,
        name='change_password'
    ),
]