from volunteer.celery import app
from django.core.mail import send_mail
@app.task
def send():
    send_mail("test?", "Ты?", 'ivanaksenov2010@mail.ru', ['ivanaksenov2010@mail.ru'])
