from celery import shared_task
from core.celery import app
from core.methods import send_mass_mail as mass_email


@shared_task
def send_mass_email_task(data) -> str:
    try:
        mass_email(data)
    except Exception as e:
        print(f'Celery error: send_mass_email_task(data)\n {e}')
        return 'Send email task failed'
    return "data"


@shared_task
def process_send_pdf_task(data) -> str:
    return "send pdf"


@app.task
def send_scheduled_emails():
    """
    To run this;
    1. Ensure  (celery -A core  worker -l INFO --pool=solo) is running
    2. Run scheduler, i.e. beat  (celery -A core  beat -l INFO )
    """
    print("doing a schedule")
    return
