import time
from time import sleep
from celery import shared_task
from django.core.mail import send_mail
from core.celery import app


@shared_task(bind=True)
def shop_task_one(bind=True):
    """Sends an email when the feedback form has been submitted."""
    # send_mail(
    #     'Test celery',
    #     'This is ent to you to test task scheduling',
    #     'pmwassini@gmil.com',
    #     ['pminnovest@gmail.com', ],
    #     fail_silently=False
    # )
    print(' **** Testing celery with expensive operations **** ')
    # time.sleep(10)
    print(' *** Expensive operation completed *** ')
    return 'Done'


@app.task
def send_scheduled_emails():
    """
    To run this;
    1. Ensure  (celery -A newsscraper  worker -l INFO --pool=solo) is running
    2. Run scheduler, i.e beat  (celery -A core  beat -l INFO --pool=solo)
    """
    print("doing a schedule")
    return
