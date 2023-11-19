from django.db import models
from django.contrib.auth.models import AbstractUser
from .manager import CustomUserManager


class CustomUser(AbstractUser):  # Creating custom user
    first_name = None
    last_name = None
    is_superuser = None
    is_staff = None
    name = models.CharField(max_length=200)
    email = models.EmailField('email_address', unique=True)
    role = models.CharField(max_length=100, default='manager')
    profile_image = models.ImageField(upload_to='profile/', blank=True, null=True)
    workspace = models.CharField(max_length=200)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    objects = CustomUserManager()
    
    def __str__(self) -> str:
        return self.email