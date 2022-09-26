from allauth.account import app_settings
from allauth.account.views import SignupView, sensitive_post_parameters_m
from allauth.account.utils import passthrough_next_redirect_url
from allauth.account.views import LoginView
from allauth.utils import get_request_param
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import redirect
from django.urls import reverse


class AccountLoginView(LoginView):

    def get_success_url(self):
        direct_to = self.request.POST.get('next', None) or self.request.GET.get('next', None)
        referer = self.request.META.get('HTTP_REFERER', None)
        if direct_to is None:
            direct_to = '/' if referer is None else referer
        if direct_to != "None" and direct_to is not None:
            url_parts = direct_to.split('/')
            if 'auth' in url_parts:
                return '/'
        return direct_to

    def get_context_data(self, **kwargs):
        ret = super(AccountLoginView, self).get_context_data(**kwargs)
        signup_url = passthrough_next_redirect_url(self.request, reverse("account_signup"), self.redirect_field_name)
        site = get_current_site(self.request)
        direct_to = self.request.POST.get('next', None) or self.request.GET.get('next', None)
        referer = self.request.META.get('HTTP_REFERER', None)
        redirect_field_value = "/"
        if referer is not None:
            redirect_field_value = referer
        if direct_to is not None:
            redirect_field_value = direct_to
        ret.update(
            {
                "signup_url": signup_url,
                "site": site,
                "redirect_field_name": self.redirect_field_name,
                "redirect_field_value": redirect_field_value,
            }
        )
        return ret


class AccountSignUpView(SignupView):

    def get_success_url(self):
        direct_to = self.request.POST.get('next', None) or self.request.GET.get('next', None)
        referer = self.request.META.get('HTTP_REFERER', None)
        if direct_to is None:
            direct_to = '/' if referer is None else referer

        if direct_to != "None" and direct_to is not None:
            url_parts = direct_to.split('/')
            if 'auth' in url_parts:
                return '/'
        return direct_to

    def get_context_data(self, **kwargs):
        ret = super(AccountSignUpView, self).get_context_data(**kwargs)
        signup_url = passthrough_next_redirect_url(self.request, reverse("account_signup"), self.redirect_field_name)
        site = get_current_site(self.request)
        direct_to = self.request.POST.get('next', None) or self.request.GET.get('next', None)
        referer = self.request.META.get('HTTP_REFERER', None)
        redirect_field_value = "/"
        if referer is not None:
            redirect_field_value = referer
        if direct_to is not None:
            redirect_field_value = direct_to
        ret.update(
            {
                "signup_url": signup_url,
                "site": site,
                "redirect_field_name": self.redirect_field_name,
                "redirect_field_value": redirect_field_value,
            }
        )
        return ret


account_signup_view = AccountSignUpView.as_view()

account_login_view = AccountLoginView.as_view()
