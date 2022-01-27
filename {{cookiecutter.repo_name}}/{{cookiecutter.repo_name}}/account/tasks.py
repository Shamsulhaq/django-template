from backend.celery import app
from backend.mail import send_mail_from_template
from backend.sms import send_otp


@app.task
def send_email_on_delay(template, context, subject, email):
    send_mail_from_template(template, context, subject, email)


@app.task
def send_otp_on_delay(phone, otp):
    send_otp(phone, otp)