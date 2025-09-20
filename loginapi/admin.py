from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField 

from .models import User

# Form for creating user
class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'name', 'role')

    def clean_password2(self):
        pw1 = self.cleaned_data.get("password1")
        pw2 = self.cleaned_data.get("password2")
        if pw1 and pw2 and pw1 != pw2:
            raise forms.ValidationError("Passwords don’t match")
        return pw2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])  # hashes password
        if commit:
            user.save()
        return user

# Form for updating user
class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'name', 'role', 'is_active', 'is_staff')

# Admin class
class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('email', 'name', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name','role')}),
        ('Permissions', {'fields': ('is_staff','is_active','is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email','name','role','password1','password2','is_staff','is_active')}
        ),
    )
    search_fields = ('email', 'name')
    ordering = ('email',)

admin.site.register(User, UserAdmin)
