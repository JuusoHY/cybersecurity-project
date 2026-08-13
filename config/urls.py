from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path


urlpatterns = [
    path('admin/', admin.site.urls),

    path(
        'accounts/login/',
        auth_views.LoginView.as_view(),
        name='account_login'
    ),
    path(
        'accounts/logout/',
        auth_views.LogoutView.as_view(),
        name='account_logout'
    ),

    path('', include('tasks.urls')),
]