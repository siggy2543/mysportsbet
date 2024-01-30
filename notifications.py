import smtplib
from email.message import EmailMessage

def send_email(user, message):
    """Sends a notification email to the user"""
    email = EmailMessage()
    email['To'] = user.email  
    email['From'] = 'notifications@example.com'
    email['Subject'] = 'Notification'  
    email.set_content(message)
    smtp = smtplib.SMTP('localhost')
    smtp.send_message(email)
    smtp.quit()

def send_push(user, message):
    """Sends a push notification to the user"""
    # API call to push service 
    push_service.notify(user.id, message)