from django.urls import path
from .views import StatsAPIView, ProfileCompletionAPIView, RecentApplicationsAPIView
from .views import SignupView, LoginView, ApplicationView, AllApplicationsView, ApplicationDetailView, ForgotPasswordView, ResetPasswordView
from .views import (
    CompanyInfoView,
    FoundingInfoView,
    SocialMediaView,
    ContactInfoView,
    CompanyCompleteView
)
from .views import JobCreateAPIView

urlpatterns = [
    # Auth
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),

    # Applications (Job Seeker)
    path("apply/", ApplicationView.as_view(), name="apply-job"),   # Apply for a job
    path("applications/", ApplicationView.as_view(), name="applications"),  # View own applications

    # Applications (Recruiter/Admin)
    path("applications/all/", AllApplicationsView.as_view(), name="all-applications"),  # View all
    path("applications/<int:pk>/", ApplicationDetailView.as_view(), name="application-detail"),  # Update status


    path('company-info/', CompanyInfoView.as_view(), name='company-info'),
    path('founding-info/<int:id>/', FoundingInfoView.as_view(), name='founding-info'),
    path('social-media/<int:id>/', SocialMediaView.as_view(), name='social-media'),
    path('contact-info/<int:id>/', ContactInfoView.as_view(), name='contact-info'),
    path('company-complete/<int:id>/', CompanyCompleteView.as_view(), name='company-complete'),

    path('stats/', StatsAPIView.as_view(), name='stats'),
    path('profile-completion/', ProfileCompletionAPIView.as_view(), name='profile-completion'),
    path('recent-applications/', RecentApplicationsAPIView.as_view(), name='recent-applications'),

    path('jobs/create/', JobCreateAPIView.as_view(), name='jobs-create'),
]
