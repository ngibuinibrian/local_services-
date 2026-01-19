from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from app import mail

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()

def send_contact_inquiry_email(inquiry):
    send_email(
        f'[Local Services] New Inquiry from {inquiry.name}',
        sender=current_app.config['MAIL_USERNAME'],
        recipients=current_app.config['ADMINS'],
        text_body=render_template('email/contact_inquiry.txt', inquiry=inquiry),
        html_body=render_template('email/contact_inquiry.html', inquiry=inquiry)
    )
