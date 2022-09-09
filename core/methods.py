"""
methods.py have simple functions that reduce the code reputation
TODO: get_current_site to be used in deployment
For this case domain was attached to different instances to mimic dynamics of domain name changes
"""
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives


# Sub methods
def get_rendered_html(template_name, context={}):
    """
    The get_rendered_html function accepts a template name and context, 
    and returns the rendered HTML of that template.
    :param template_name: Specify the name of the template file to be rendered
    :param context={}: Pass in the dictionary of values that will be available to the template
    :return: The rendered html content of the template
    :doc-author: Trelent
    """
    html_content = render_to_string(template_name, context)
    return html_content


# Exported methods
def send_email(subject, html_content= None, text_content=None, from_email=None, recipients=[], attachments=[], bcc=[], cc=[], html_and_context = None):
    """
    The send_email function sends an email to a user with a link to reset their password.
    The function takes the following arguments:
        subject - The subject of the email. Defaults to 'Password Reset Request' if not provided.
        html_content - The HTML content of the email body, which should contain a link for password resetting. 
            If no HTML is provided, then only text will be sent in the body of the message (not recommended). 
            This argument can also be passed as None and instead passed as an additional argument called context, 
            which is expected to be a dictionary containing all necessary information
    
    :param subject: Set the subject of the email
    :param html_content: Pass in the html content of the email
    :param text_content=None: Specify the text version of the email
    :param from_email=None: Specify the email address that will be shown as the sender of the email
    :param recipients=[]: Specify the recipients of the email
    :param attachments=[]: Attach files to the email
    :param bcc=[]: Send emails to a list of recipients without them being exposed in the email's &quot;to&quot; field
    :param cc=[]: Send carbon copies to other email addresses
    :param html_and_context=None: Pass in a dictionary of context variables that will be used to render the html template
    :return: None
    :doc-author: Trelent
    """
    
    # send email to user with attachment
    if not from_email:
        from_email = settings.ALLOWED_EMAIL[0]
    if not text_content:
        text_content = ''
    email = EmailMultiAlternatives(
        subject, text_content, from_email, recipients, bcc=bcc, cc=cc
    )
    if html_and_context is not None:
        html_content = get_rendered_html(html_and_context['template_name'], html_and_context['context'])
    if html_content is not None:     
        email.attach_alternative(html_content, "text/html")
    for attachment in attachments:
        # Example: email.attach('design.png', img_data, 'image/png')
        email.attach(*attachment)
    email.send()


def send_mass_mail(data_list):
    """
    The send_mass_mail function accepts a list of dictionaries, each containing a template and context. 
    The function then loops through the list, rendering HTML from each template using the provided context. 
    Finally, it uses the EmailMultiAlternatives function to send each message to its recipient.
    :param data_list: Pass a list of dictionaries to the send_mass_mail function
    :return: A list of the sent email messages
    :doc-author: Trelent
    """
    for data in data_list:
        template = data.pop('template')
        context = data.pop('context')
        html_content = get_rendered_html(template, context)
        data.update({'html_content': html_content})
        send_email(**data)
