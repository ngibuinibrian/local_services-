import os
import africastalking
from twilio.rest import Client
from flask import current_app

def send_sms_at(to, message):
    """Sends SMS via Africa's Talking"""
    username = os.environ.get('AT_USERNAME', 'sandbox')
    api_key = os.environ.get('AT_API_KEY')
    if not api_key:
        return False
    try:
        africastalking.initialize(username, api_key)
        response = africastalking.SMS.send(message, [to])
        current_app.logger.info(f"AT SMS response: {response}")
        return True
    except Exception as e:
        current_app.logger.error(f"AT SMS Error: {str(e)}")
        return False

def send_sms_twilio(to, message):
    """Sends SMS via Twilio"""
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    from_number = os.environ.get('TWILIO_FROM_NUMBER')
    if not (account_sid and auth_token and from_number):
        return False
    try:
        client = Client(account_sid, auth_token)
        client.messages.create(body=message, from_=from_number, to=to)
        return True
    except Exception as e:
        current_app.logger.error(f"Twilio SMS Error: {str(e)}")
        return False

def send_sms(to, message):
    """
    Main entry point for SMS. 
    Checks for Twilio first if AT fails or is not configured.
    """
    provider = os.environ.get('SMS_PROVIDER', 'at').lower()
    
    success = False
    if provider == 'twilio':
        success = send_sms_twilio(to, message)
    else:
        success = send_sms_at(to, message)
        # Fallback to Twilio if AT fails and Twilio is configured
        if not success:
            success = send_sms_twilio(to, message)

    if not success:
        current_app.logger.error("All SMS providers failed.")
    return success

def notify_admin_new_request(service_request):
    admin_phone = os.environ.get('ADMIN_PHONE')
    if admin_phone:
        message = f"New Service Request #{service_request.id}\nFrom: {service_request.full_name}\nService: {service_request.service_needed}"
        send_sms(admin_phone, message)

def notify_customer_status_update(service_request):
    message = f"Hello {service_request.full_name}, your request for {service_request.service_needed} is now: {service_request.status}."
    send_sms(service_request.phone, message)
