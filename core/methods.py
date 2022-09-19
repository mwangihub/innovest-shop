"""
methods.py have simple functions that reduce the code reputation
TODO: get_current_site to be used in deployment
For this case domain was attached to different instances to mimic dynamics of domain name changes
"""
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

User = get_user_model()


# Sub methods
def get_rendered_html(template_name, context={}):
    html_content = render_to_string(template_name, context)
    return html_content


# Exported methods
def send_email(subject, html_content=None, text_content=None, from_email=None, recipients=[], attachments=[], bcc=[], cc=[]):
    if not from_email:
        from_email = settings.DEFAULT_FROM_EMAIL
    if not text_content:
        text_content = ''
    email = EmailMultiAlternatives(
        subject, text_content, from_email, recipients, bcc=bcc, cc=cc
    )
    if html_content:
        email.attach_alternative(html_content, "text/html")
    for attachment in attachments:
        email.attach(attachment.name, attachment.read(), attachment.content_type)
    email.send()


def send_mass_mail(data_list):
    for data in data_list:
        template = data.pop('template')
        context = data.pop('context')
        html_content = get_rendered_html(template, context)
        data.update({'html_content': html_content})
        send_email(**data)


def _user(request=None):
    if not settings.DEV_MODE:
        return request.user
    return User.objects.get(email="pmwassini@gmail.com")


def app_active_check(name):
    from user.models import Project
    try:
        app_active = Project.objects.get(alias_name=name)
        if not app_active.display:
            return True
    except Project.DoesNotExist:
        raise NotImplementedError(f"{name} App (app_name) is not saved in projects table. This will allow "
                                  "unauthorized view of the page which is uncompleted project.")
    return False
