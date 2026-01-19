import africastalking
import os
from flask import current_app

def send_sms(to, message):
    """
    Sends an SMS using Africa's Talking API.
    'to' should be in international format (e.g., +254711222333).
    """
    username = os.environ.get('AT_USERNAME', 'sandbox')
    api_key = os.environ.get('AT_API_KEY')
    
    if not api_key:
        current_app.logger.warning("AT_API_KEY not set. SMS not sent.")
        return False

    africastalking.initialize(username, api_key)
    sms = africastalking.SMS

    try:
        response = sms.send(message, [to])
        current_app.logger.info(f"SMS sent to {to}: {response}")
        return True
    except Exception as e:
        current_app.logger.error(f"Error sending SMS: {str(e)}")
        return False

def notify_admin_new_request(service_request):
    admin_phone = os.environ.get('ADMIN_PHONE')
    if admin_phone:
        message = f"New Service Request #{service_request.id}\nFrom: {service_request.full_name}\nService: {service_request.service_needed}\nLocation: {service_request.location}\nPhone: {service_request.phone}"
        send_sms(admin_phone, message)

def notify_customer_status_update(service_request):
    message = f"Hello {service_request.full_name}, your request for {service_request.service_needed} has been updated to: {service_request.status}."
    send_sms(service_request.phone, message)
