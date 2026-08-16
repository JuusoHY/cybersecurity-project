from django.contrib.auth.models import User
from django.db import models


class Task(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# FLAW 5: A3:2017 Sensitive Data Exposure
# This model stores the user's plaintext password in the database.
# If the database is compromised, all passwords are immediately exposed.
class UserSecret(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plaintext_password = models.CharField(max_length=255)


# FIX: Remove the UserSecret model above entirely. Django's User model
# already stores a hashed password securely. No plaintext copy is needed.