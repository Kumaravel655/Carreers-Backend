from rest_framework.decorators import api_view
from .serializers import UserSerializer, LoginSerializer
from .models import User

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from .models import Job, Application, Notification
from .serializers import JobSerializer, ApplicationSerializer, NotificationSerializer


# ---------------- Signup ----------------
@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(
            {"message": "User created successfully", "user": UserSerializer(user).data},
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------------- Login ----------------
@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')
    user = User.objects.filter(email=email).first()

    if not user:
        user = User.objects.create_user(email=email, password=password, role='employee')

    return Response({
        "message": "Login successful",
        "email": user.email,
        "role": user.role
    }, status=status.HTTP_200_OK)

# ---------------- Job Detail API ----------------
class JobDetailView(generics.RetrieveAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    lookup_field = "id"


# ---------------- Apply Job API ----------------
class ApplyJobView(APIView):
    def post(self, request, job_id):
        data = request.data
        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)

        data["job"] = job.id
        serializer = ApplicationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------------- Application Status API ----------------
class ApplicationStatusView(generics.RetrieveAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    lookup_field = "id"


# ---------------- Notifications API ----------------
class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        user_id = self.request.query_params.get("user_id")
        if user_id:
            return Notification.objects.filter(user_id=user_id).order_by("-created_at")
        return Notification.objects.none()
