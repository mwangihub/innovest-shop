from allauth.account.adapter import get_adapter
from allauth.account import app_settings
# from allauth.account.app_settings import AuthenticationMethod
from allauth.account.utils import user_username, user_email, setup_user_email, filter_users_by_email, user_pk_to_url_str
from allauth.utils import set_form_field_order, build_absolute_uri
from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse

from .models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.translation import gettext_lazy as _

# allauth forms
from allauth.account.forms import LoginForm, BaseSignupForm, default_token_generator, ChangePasswordForm
from allauth.socialaccount.forms import SignupForm


# ALLAUTH OVERRIDE
class PasswordField(forms.CharField):
    def __init__(self, *args, **kwargs):
        kwargs["widget"] = forms.PasswordInput(render_value=False, attrs={"placeholder": "", "class": "did-floating-input"})
        autocomplete = kwargs.pop("autocomplete", None)
        if autocomplete is not None:
            kwargs["widget"].attrs["autocomplete"] = autocomplete
        super(PasswordField, self).__init__(*args, **kwargs)


class CustomAuthForm(LoginForm):

    def __init__(self, *args, **kwargs):
        # overriding stylings
        super().__init__(*args, **kwargs)
        self.fields['login'].widget.attrs.update({'class': 'did-floating-input', 'placeholder': ""})
        self.fields['login'].label = "Email address"
        self.fields['password'].widget.attrs.update({'class': 'did-floating-input', 'placeholder': ""})
        self.fields['password'].label = "Password"
        if settings.ACCOUNT_SESSION_REMEMBER is None:
            self.fields['remember'].widget.attrs.update({'class': 'form-check-input', 'role': "switch"})


class CustomAuthSocialForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'form-control rounded-4',
            'placeholder': "E-mail address"
        })
        self.fields['email'].label = "Your email"

    def save(self, request):
        user = super(CustomAuthSocialForm, self).save(request)
        # Add your own processing here.
        # You must return the original result.
        return user


class RegisterForm(BaseSignupForm):
    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields["password1"] = PasswordField(label="Password", autocomplete="new-password")
        self.fields["password2"] = PasswordField(label="Password (again)", autocomplete="new-password")
        self.fields["email"].widget.attrs.update({'class': 'did-floating-input', 'placeholder': ""})
        self.fields['email'].label = "Email address"
        if hasattr(self, "field_order"):
            set_form_field_order(self, self.field_order)

    def clean(self):
        super(RegisterForm, self).clean()
        # `password` cannot be of type `SetPasswordField`, as we don't
        # have a `User` yet. So, let's populate a dummy user to be used
        # for password validation.
        dummy_user = User()
        user_username(dummy_user, self.cleaned_data.get("username"))
        user_email(dummy_user, self.cleaned_data.get("email"))
        password = self.cleaned_data.get("password1")
        if password:
            try:
                get_adapter().clean_password(password, user=dummy_user)
            except forms.ValidationError as e:
                self.add_error("password1", e)

        if "password1" in self.cleaned_data and "password2" in self.cleaned_data:
            if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
                self.add_error("password2", "You must type the same password each time.")
        return self.cleaned_data

    def save(self, request):
        adapter = get_adapter(request)
        user = adapter.new_user(request)
        adapter.save_user(request, user, self)
        self.custom_signup(request, user)
        # TODO: Move into adapter `save_user` ?
        setup_user_email(request, user, [])
        return user


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(
        label=_("E-mail"),
        required=True,
        widget=forms.TextInput(
            attrs={
                "type": "email",
                "class": "did-floating-input",
                "placeholder": "",
                "autocomplete": "email",
            }
        ),
    )

    def clean_email(self):
        email = self.cleaned_data["email"]
        email = get_adapter().clean_email(email)
        self.users = filter_users_by_email(email, is_active=True)
        if not self.users and not app_settings.PREVENT_ENUMERATION:
            raise forms.ValidationError(
                _("The e-mail address is not assigned to any user account")
            )
        return self.cleaned_data["email"]

    def save(self, request, **kwargs):
        email = self.cleaned_data["email"]
        if not self.users:
            self._send_unknown_account_mail(request, email)
        else:
            self._send_password_reset_mail(request, email, self.users, **kwargs)
        return email

    def _send_unknown_account_mail(self, request, email):
        signup_url = build_absolute_uri(request, reverse("account_signup"))
        context = {
            "current_site": get_current_site(request),
            "email": email,
            "request": request,
            "signup_url": signup_url,
        }
        get_adapter(request).send_mail("account/email/unknown_account", email, context)

    def _send_password_reset_mail(self, request, email, users, **kwargs):
        token_generator = kwargs.get("token_generator", default_token_generator)

        for user in users:

            temp_key = token_generator.make_token(user)
            # save it to the password reset model
            # password_reset = PasswordReset(user=user, temp_key=temp_key)
            # password_reset.save()
            # send the password reset email
            path = reverse(
                "account_reset_password_from_key",
                kwargs=dict(uidb36=user_pk_to_url_str(user), key=temp_key),
            )
            url = build_absolute_uri(request, path)

            context = {
                "current_site": get_current_site(request),
                "user": user,
                "password_reset_url": url,
                "request": request,
            }

            if app_settings.AUTHENTICATION_METHOD != app_settings.AuthenticationMethod.EMAIL:
                context["username"] = user_username(user)
            get_adapter(request).send_mail(
                "account/email/password_reset_key", email, context
            )


class PasswordChangeForm(ChangePasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['oldpassword'].widget.attrs.update({'class': 'did-floating-input', 'placeholder': ""})
        self.fields['password1'].widget.attrs.update({'class': 'did-floating-input', 'placeholder': ""})
        self.fields['password2'].widget.attrs.update({'class': 'did-floating-input', 'placeholder': ""})


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
    the user, but replaces the password field with admins
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = '__all__'

    def clean_password(self):
        return self.initial["password"]


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


# ###################################

class RegisterFormR(forms.ModelForm):
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
        user = super(RegisterFormR, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class PasswordResetRequestFormR(forms.Form):
    email = forms.EmailField(label="Email", max_length=254)
