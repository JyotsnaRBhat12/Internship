from django.db import models
from django.contrib.auth.models import User
import uuid


class Note(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    title = models.CharField(max_length=200)

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class SharedLink(models.Model):

    note = models.ForeignKey(Note, on_delete=models.CASCADE)

    token = models.UUIDField(default=uuid.uuid4, unique=True)

    expiry_date = models.DateTimeField(null=True, blank=True)

    access_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)