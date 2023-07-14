from celery import shared_task
from core.celery import app
from core.methods import send_mass_mail, send_email


@shared_task(bind=True)
def send_mass_email(data: list, bind: bool = True) -> str:
    """Sends an email when the feedback form has been submitted.
        message = {
        'subject': f'New Message: {data.get("email")}',
        'recipients': ['pminnovest@gmail.com', ],
        'template': "email/gtgMessage/gtgMessage.html",
        'context': {'message': data, },
        'attachments': None
    }
    data=[message, ]
    """
    send_mass_mail(data)
    return 'Done'


@app.task
def send_scheduled_emails():
    """
    To run this;
    1. Ensure  (celery -A core  worker -l INFO --pool=solo) is running
    2. Run scheduler, i.e. beat  (celery -A core  beat -l INFO )
    """
    print("doing a schedule")
    return
