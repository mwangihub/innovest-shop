from django.conf import settings
from allauth.account.adapter import DefaultAccountAdapter as AllauthAdapter
# allauth.account.adapter.DefaultAccountAdapter:
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter as SocialAdapter

word_before = lambda sentence, word: sentence.split()[sentence.split().index(
    word) - 1] if word in sentence else None


class DefaultAccountAdapter(AllauthAdapter):

    def save_user(self, request, user, form, commit=True):
        """
        Saves a new `User` instance using information provided in the
        signup form.
        """
        from allauth.account.utils import user_email, user_field, user_username
        data = form.cleaned_data
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        email = data.get("email")
        username = data.get("username")
        buyer = data.get("buyer", None)
        user_email(user, email)
        user_username(user, username)
        if first_name:
            user_field(user, "first_name", first_name)
        if buyer:
            user_field(user, "buyer", buyer)
            user_field(user, "non", False)
        if last_name:
            user_field(user, "last_name", last_name)
        if settings.ACCOUNT_VERIFIED_ON_SIGNUP:
            user.is_active = settings.ACCOUNT_VERIFIED_ON_SIGNUP
        if "password1" in data:
            user.set_password(data["password1"])
        else:
            user.set_unusable_password()
        self.populate_username(request, user)
        if commit:
            user.save()
        return user


class CustomSocialAccountAdapter(SocialAdapter):

    def save_user(self, request, sociallogin, form):
        user = super(CustomSocialAccountAdapter, self).save_user(request, sociallogin, form)
        user.buyer = True
        user.non = False
        user.save()
        return user

    def populate_user(self, request, sociallogin, data):
        from allauth.account.utils import user_email, user_field, user_username
        from allauth.utils import valid_email_or_none, email_address_exists
        username = data.get("username")
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        email = data.get("email")
        name = data.get("name")
        buyer = data.get("buyer", None)
        non = data.get("non", None)
        user = sociallogin.user
        user_username(user, username or "")
        user_email(user, valid_email_or_none(email) or "")
        name_parts = (name or "").partition(" ")
        user_field(user, "first_name", first_name or name_parts[0])
        user_field(user, "last_name", last_name or name_parts[2])
        if buyer:
            user_field(user, "buyer", buyer)
            user_field(user, "non", non)
        # activating social account instead of doing it in the DB
        user.is_active = True
        return user
