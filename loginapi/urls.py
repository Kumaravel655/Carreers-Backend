from django.urls import path
from .views import signup, login, JobDetailView, ApplyJobView, ApplicationStatusView, NotificationListView

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', login, name='login'),
    path('jobs/<int:id>/', JobDetailView.as_view(), name='job-detail'),
    path('jobs/<int:job_id>/apply/', ApplyJobView.as_view(), name='apply-job'),
    path('applications/<int:id>/', ApplicationStatusView.as_view(), name='application-status'),
    path('notifications/', NotificationListView.as_view(), name='notifications'),
]
