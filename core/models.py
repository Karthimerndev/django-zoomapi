from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now, timedelta

class User(AbstractUser):
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password']

    def __str__(self):
        return self.email

class Meeting(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Creator
    title = models.CharField(max_length=255)
    description = models.TextField()
    date_time = models.DateTimeField()
    zoom_meeting_id = models.CharField(max_length=255, blank=True, null=True)
    join_url = models.URLField(blank=True, null=True)
    participants = models.ManyToManyField(User, related_name='invited_meetings')

    def __str__(self):
        return self.title


class ZoomToken(models.Model):
    access_token = models.TextField()
    refresh_token = models.TextField()
    expires_at = models.DateTimeField()

    def is_expired(self):
        return now() >= self.expires_at