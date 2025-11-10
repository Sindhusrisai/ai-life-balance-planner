import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

SMTP_SERVER = os.getenv("EMAIL_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("EMAIL_PORT", "587"))
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "").strip().strip('"')
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "").strip().strip('"')

def send_email_notification(receiver_email: str, subject: str, body: str):
    """
    Send an email to the given receiver with the provided subject and body.
    """
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        raise ValueError("❌ Email credentials are not set properly in .env")

    if not receiver_email:
        raise ValueError("❌ Receiver email is empty")

    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print(f"✅ Email sent successfully to {receiver_email}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        raise
