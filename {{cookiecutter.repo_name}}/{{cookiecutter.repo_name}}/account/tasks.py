from {{cookiecutter.repo_name}}.celery import app
from {{cookiecutter.repo_name}}.mail import send_mail_from_template
from {{cookiecutter.repo_name}}.sms import send_otp


@app.task
def send_email_on_delay(template, context, subject, email):
    send_mail_from_template(template, context, subject, email)


@app.task
def send_otp_on_delay(phone, otp):
    send_otp(phone, otp)