from django.contrib.auth.models import User
from django.db import models


class Task(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'login'