from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
import uuid
from django.utils import timezone
from datetime import timedelta


def one_hour_from_now():
    return timezone.now() + timedelta(hours=1)
class PasswordResetToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=one_hour_from_now)


    def __str__(self):
        return f"{self.user.email} - {self.token}"

# ---------------------------
# Custom User Model
# ---------------------------
class User(AbstractUser):
    ROLE_CHOICES = [
        ("Job Seeker", "Job Seeker"),
        ("Recruiter", "Recruiter"),
        ("Admin", "Admin"),
    ]
    username = models.CharField(max_length=150, unique=False, blank=True, null=True)
    name = models.CharField(max_length=150, blank=True)   # Full Name
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="Job Seeker")
    profile_complete = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return f"{self.email} ({self.role})"


# ---------------------------
# Company Model
# ---------------------------
class Company(models.Model):
    name = models.CharField(max_length=255)
    industry = models.CharField(max_length=255)
    website = models.URLField(blank=True, null=True)
    founder_name = models.CharField(max_length=255, blank=True, null=True)
    founded_year = models.IntegerField(blank=True, null=True)
    headquarters = models.CharField(max_length=255, blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, default="incomplete")  # incomplete or completed

    def __str__(self):
        return self.name


# ---------------------------
# Job Model
# ---------------------------
class Job(models.Model):
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255, blank=True)
    recruiter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="jobs")
    tags = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=100, blank=True)

    min_salary = models.IntegerField(null=True, blank=True)
    max_salary = models.IntegerField(null=True, blank=True)
    salary_type = models.CharField(max_length=50, blank=True)

    education = models.CharField(max_length=100, blank=True)
    experience = models.CharField(max_length=100, blank=True)
    job_type = models.CharField(max_length=50, blank=True)
    job_level = models.CharField(max_length=50, blank=True)

    vacancies = models.IntegerField(null=True, blank=True)
    expiration_date = models.DateField(null=True, blank=True)

    location_country = models.CharField(max_length=100, blank=True)
    location_city = models.CharField(max_length=100, blank=True)
    is_remote = models.BooleanField(default=False)

    benefits = models.JSONField(default=list, blank=True)
    description = models.TextField(blank=True)
    apply_method = models.CharField(max_length=50, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} at {self.recruiter.username}"


# ---------------------------
# Job Application Model
# ---------------------------
class Application(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="applications")
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    resume = models.FileField(upload_to="resumes/")
    cover_letter = models.TextField(blank=True)
    status = models.CharField(
        max_length=50,
        choices=[('pending','Pending'),('accepted','Accepted'),('rejected','Rejected')],
        default='pending'
    )
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.job.title}"
