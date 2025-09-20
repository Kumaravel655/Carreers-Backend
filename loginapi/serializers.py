# Login 
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from .models import Application
from .models import User
from .models import Company
from .models import Job

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "role"]

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    role = serializers.CharField()

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")
        role = data.get("role")

        user = authenticate(username=email, password=password)
        if user is None:
            raise serializers.ValidationError("Invalid credentials!")

        if user.role != role:
            raise serializers.ValidationError("Role mismatch!")

        return user


# SignUp

class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "name", "email", "password", "role"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)

# ---------------- Forgot Password ----------------
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

# ---------------- Reset Password ----------------
class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        validate_password(data['new_password'])
        return data


# ApplyJob


class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = [
            "id", "job", "applicant", "name", "email", "phone",
            "resume", "cover_letter", "status", "applied_at"
        ]
        read_only_fields = ["status", "applied_at"]

# Company


class CompanyInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'industry', 'website']

class FoundingInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'founder_name', 'founded_year', 'headquarters']

class SocialMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'linkedin', 'twitter']

class ContactInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'email', 'phone', 'address']

class CompanyCompleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'status']



# Recent applications serializer
class RecentApplicationSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='job.title')
    company = serializers.CharField(source='job.company')
    logoColor = serializers.SerializerMethodField()
    type = serializers.CharField(source='job.type')
    location = serializers.CharField(source='job.location')
    salary = serializers.CharField(source='job.salary')
    date = serializers.DateTimeField(source='applied_on', format="%Y-%m-%d")
    
    class Meta:
        model = Application
        fields = ['title', 'company', 'logoColor', 'type', 'location', 'salary', 'date', 'status']

    def get_logoColor(self, obj):
        # Example: generate color based on company name hash
        colors = ['#f56a00', '#7265e6', '#ffbf00', '#00a2ae']
        return colors[hash(obj.job.company) % len(colors)]




class JobCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'
        read_only_fields = ['id', 'recruiter']

    def create(self, validated_data):
        validated_data['recruiter'] = self.context['request'].user
        return super().create(validated_data)
