from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ttam_token = models.CharField(max_length=1000, null=True)
    fitbit_token = models.CharField(max_length=1000, null=True)
    facebook_token = models.CharField(max_length=1000, null=True)
