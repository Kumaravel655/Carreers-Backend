from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, permissions, status
from .serializers import UserSerializer, SignupSerializer, ApplicationSerializer, RecentApplicationSerializer, Company, JobCreateSerializer
from rest_framework.permissions import IsAuthenticated
from .models import User, Job, Application

from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from .serializers import ForgotPasswordSerializer, ResetPasswordSerializer
from .models import PasswordResetToken

# -----------------------------
# SIGNUP VIEW
# -----------------------------
class SignupView(APIView):
    def post(self, request):
        email = request.data.get('email')

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)

        # Optional: check if password and confirm_password match
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')
        if password != confirm_password:
            return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  # create the user
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -----------------------------
# LOGIN VIEW
# -----------------------------
class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        role = request.data.get('role')

        user = authenticate(request, email=email, password=password)

        if not email or not password or not role:
            return Response({"error": "Email, password, and role are required"}, status=status.HTTP_400_BAD_REQUEST)

        if not user:
            return Response({"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)

        if user.role != role:
            return Response({"error": "Role mismatch"}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        return Response({
            "user": UserSerializer(user).data,
            "token": str(refresh.access_token)
        }, status=status.HTTP_200_OK)

class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                token_obj = PasswordResetToken.objects.create(user=user)
                # Send email (console backend will print)
                send_mail(
                    subject="Password Reset Token",
                    message=f"Use this token to reset your password: {token_obj.token}",
                    from_email="noreply@example.com",
                    recipient_list=[user.email],
                    fail_silently=False
                )
                return Response({"message": "Password reset token sent to email"})
            except User.DoesNotExist:
                return Response({"error": "User with this email does not exist"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            new_password = serializer.validated_data['new_password']

            try:
                token_obj = PasswordResetToken.objects.get(token=token)
            except PasswordResetToken.DoesNotExist:
                return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

            if token_obj.expires_at < timezone.now():
                return Response({"error": "Token expired"}, status=status.HTTP_400_BAD_REQUEST)

            user = token_obj.user
            user.set_password(new_password)
            user.save()
            token_obj.delete()
            return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ApplyJob

# ----------------------------
# Job Seeker: Apply & View Own Applications
# ----------------------------
class ApplicationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    # Apply for a job
    def post(self, request):
        serializer = ApplicationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(applicant=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Get only the logged-in user’s applications
    def get(self, request):
        apps = Application.objects.filter(applicant=request.user)
        serializer = ApplicationSerializer(apps, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ----------------------------
# Recruiter/Admin: Manage Applications
# ----------------------------
class AllApplicationsView(generics.ListAPIView):
    queryset = Application.objects.all().order_by("-applied_at")
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAdminUser | permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Recruiter: show only applications for jobs they posted
        if hasattr(user, "role") and user.role == "Recruiter":
            return Application.objects.filter(job__posted_by=user).order_by("-applied_at")
        # Admin: show all
        return super().get_queryset()


class ApplicationDetailView(generics.RetrieveUpdateAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAdminUser | permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        """Recruiter/Admin can update application status only"""
        application = self.get_object()
        new_status = request.data.get("status")

        if new_status not in ["Pending", "Accepted", "Rejected"]:
            return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

        application.status = new_status
        application.save()
        serializer = self.get_serializer(application)
        return Response(serializer.data, status=status.HTTP_200_OK)


from .serializers import (
    CompanyInfoSerializer,
    FoundingInfoSerializer,
    SocialMediaSerializer,
    ContactInfoSerializer,
    CompanyCompleteSerializer
)

# Step 1: Company Info
class CompanyInfoView(generics.CreateAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanyInfoSerializer

# Step 2: Founding Info
class FoundingInfoView(generics.UpdateAPIView):
    queryset = Company.objects.all()
    serializer_class = FoundingInfoSerializer
    lookup_field = 'id'

# Step 3: Social Media
class SocialMediaView(generics.UpdateAPIView):
    queryset = Company.objects.all()
    serializer_class = SocialMediaSerializer
    lookup_field = 'id'

# Step 4: Contact Info
class ContactInfoView(generics.UpdateAPIView):
    queryset = Company.objects.all()
    serializer_class = ContactInfoSerializer
    lookup_field = 'id'

# Step 5: Complete Profile
class CompanyCompleteView(generics.UpdateAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanyCompleteSerializer
    lookup_field = 'id'

    def patch(self, request, *args, **kwargs):
        company = self.get_object()
        company.status = "completed"
        company.save()
        return Response({"status": "completed"})





# Role-based stats
class StatsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        role = user.role

        if role == 'admin':
            data = [
                {"title": "Total Jobs", "value": Job.objects.count(), "icon": "applied"},
                {"title": "Total Users", "value": User.objects.count(), "icon": "favorite"},
                {"title": "Total Applications", "value": Application.objects.count(), "icon": "alert"},
            ]
        elif role == 'recruiter':
            jobs_posted = Job.objects.filter(recruiter=user).count()
            applicants_count = Application.objects.filter(job__recruiter=user).count()
            pending_apps = Application.objects.filter(job__recruiter=user, status='pending').count()
            data = [
                {"title": "Jobs Posted", "value": jobs_posted, "icon": "applied"},
                {"title": "Applicants", "value": applicants_count, "icon": "favorite"},
                {"title": "Pending Applications", "value": pending_apps, "icon": "alert"},
            ]
        else:  # jobseeker
            jobs_applied = Application.objects.filter(applicant=user).count()
            accepted = Application.objects.filter(applicant=user, status='accepted').count()
            rejected = Application.objects.filter(applicant=user, status='rejected').count()
            pending = Application.objects.filter(applicant=user, status='pending').count()
            data = [
                {"title": "Jobs Applied", "value": jobs_applied, "icon": "applied"},
                {"title": "Accepted", "value": accepted, "icon": "favorite"},
                {"title": "Rejected", "value": rejected, "icon": "alert"},
                {"title": "Pending", "value": pending, "icon": "applied"},
            ]

        return Response(data)


# Profile completion API
class ProfileCompletionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "profile_complete": user.profile_complete,
            "message": "Complete your profile editing & build your custom Resume" if not user.profile_complete else ""
        })


# Recent applications API
class RecentApplicationsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        role = user.role

        if role == 'recruiter':
            queryset = Application.objects.filter(job__recruiter=user).order_by('-applied_on')[:5]
        elif role == 'jobseeker':
            queryset = Application.objects.filter(applicant=user).order_by('-applied_on')[:5]
        else:  # admin sees all
            queryset = Application.objects.all().order_by('-applied_on')[:5]

        serializer = RecentApplicationSerializer(queryset, many=True)
        return Response(serializer.data)



class JobCreateAPIView(generics.CreateAPIView):
    serializer_class = JobCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(recruiter=self.request.user)
