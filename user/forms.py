from django import forms
from django.conf import settings
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.translation import gettext_lazy as _

# allauth forms
from allauth.account.forms import LoginForm
from allauth.socialaccount.forms import SignupForm

class CustomAuthForm(LoginForm):

    def __init__(self, *args, **kwargs):
        # overriding stylings
        super().__init__(*args, **kwargs)
        self.fields['login'].widget.attrs.update({
            'class':
            'form-control rounded-4',
            'placeholder':
            "E-mail address"
        })
        self.fields['login'].label = "E-mail address"
        self.fields['password'].widget.attrs.update({
            'class': 'form-control rounded-4',
            'placeholder': "Password"
        })
        if settings.ACCOUNT_SESSION_REMEMBER is None:
            self.fields['remember'].widget.attrs.update({
                'class': 'form-check-input',
                'role': "switch"
            })

class CustomAuthSocialForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
                    'class':'form-control rounded-4',
                    'placeholder':"E-mail address"
                })
        self.fields['email'].label = "Your email"
        
        
    def save(self, request):
        user = super(CustomAuthSocialForm, self).save(request)
        # Add your own processing here.
        # You must return the original result.
        return user
    
    
# App forms

class CustomAuthForm1(AuthenticationForm):
    '''
    My original custom login form
    '''

    def __init__(self, *args, **kwargs):
        # overriding stylings
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class':
            'form-control rounded-4',
            'placeholder':
            "E-mail address"
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control rounded-4',
            'placeholder': "Password"
        })

    class Meta:
        model = User
        fields = ['username', 'password']


class RegisterForm(forms.ModelForm):
    field_order = [
        "email",
        'first_name',
        'last_name',
        "password1",
        "password2",
    ]

    class Meta:
        model = User
        fields = ["email", 'first_name', 'last_name']

    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class EmployeeSignUpForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.employee = True
        if commit:
            user.save()
        return user


class CustomerSignUpForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.buyer = True
        if commit:
            user.save()
        return user


class UserAdminCreationForm(forms.ModelForm):
    """
    A form for creating new users. Includes all the required
    fields, plus a repeated password.
    """
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation',
                                widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = "__all__"

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super(UserAdminCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserAdminChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = '__all__'

    def clean_password(self):
        return self.initial["password"]


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=254)


class SetPasswordForm(forms.Form):
    error_messages = {
        'password_mismatch': "The two password fields didn't match.",
    }
    new_password1 = forms.CharField(label="New password",
                                    widget=forms.PasswordInput)
    new_password2 = forms.CharField(label="New password confirmation",
                                    widget=forms.PasswordInput)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        return password2
