from django.db import models
from django.contrib.auth.models import AbstractUser

# Custom User Model with Role
class User(AbstractUser):
    ROLE_CHOICES = (
        ('regular', 'Regular User'),
        ('admin', 'Admin'),
        ('employee', 'Employee'),
        ('manager', 'Manager'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='regular')

    def __str__(self):
        return f"{self.username} ({self.role})"
