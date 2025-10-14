from django.db import models

# Create your models here.
class UserProfile(models.Model):
    username: str
    email: str
    password: str