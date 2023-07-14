"""
methods.py have simple functions that reduce the code reputation
TODO: get_current_site to be used in deployment
For this case domain was attached to different instances to mimic dynamics of domain name changes
"""
import json
import random
import string

from asgiref.sync import async_to_sync as sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

channel_layer = get_channel_layer()
User = get_user_model()


def send_channel_message(data, channel_name=None, function_name=None):
    """
        send_channel_message({
            'data': titles,
            'notification': f"{buyer} just purchased: ",
            'type': Order.__name__,
        }, channel_name='shop', function_name='send_new_item')
    """
    sync(channel_layer.group_send)(
        f'{channel_name}', {
            'type': f'{function_name}',
            'text': data
        })


# Sub methods
def get_rendered_html(template_name, context={}):
    html_content = render_to_string(template_name, context)
    return html_content


# Exported methods
def send_email(
        subject=None,
        html_content=None,
        text_content=None,
        from_email=None,
        recipients=[],
        attachments=[],
        bcc=[],
        cc=[]
):
    if not from_email:
        from_email = settings.DEFAULT_FROM_EMAIL
    if not text_content:
        text_content = ''
    email = EmailMultiAlternatives(
        subject,
        text_content,
        from_email,
        recipients,
        bcc=bcc,
        cc=cc
    )
    if html_content:
        email.attach_alternative(html_content, "text/html")
    for attachment in attachments:
        email.attach(attachment.name, attachment.read(), attachment.content_type)
    try:
        email.send()
    except Exception as e:
        print('Error: email.send()')


def send_mass_mail(data_list):
    for data in data_list:
        template = data.pop('template')
        context = data.pop('context')
        json_data = data.pop('json', None)
        if json_data:
            context["object"] = json.loads(json_data)
        html_content = get_rendered_html(template, context)
        data.update({'html_content': html_content})
        send_email(**data)


def _user(request=None):
    """
    Get use base on Development mode. If settings.DEV_MODE return existing user
    for the purpose of development.
    """
    if not settings.DEV_MODE:
        return request.user
    try:
        return User.objects.get(email="petermwangi@gmail.com")
    except Exception as e:
        return User.objects.all().first()


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


def create_unique_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=20))
