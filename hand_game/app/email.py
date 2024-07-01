from django.conf import settings
from django.core.mail import send_mail


    
def sendotp(email,otp):
    subject = 'Verify email'
    user_otp = str(otp)
    message = "Hello,\n\nWelcome to the game world,\n verify your email to start ,\n\n your otp is: "+user_otp 
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)
