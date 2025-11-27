import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def send_final_test():
    try:
        # Configuration
        email = os.getenv('EMAIL_USERNAME')
        password = os.getenv('GMAIL_APP_PASSWORD')
        recipient = os.getenv('ADMIN_EMAIL')
        
        if not all([email, password, recipient]):
            raise ValueError("Missing required environment variables")

        # Create message
        msg = MIMEMultipart()
        msg['From'] = email
        msg['To'] = recipient
        msg['Subject'] = "Final Success Test"
        
        body = "This email confirms your Flask app can now send emails successfully!"
        msg.attach(MIMEText(body, 'plain'))

        # Send email (using the port that worked in your connection test)
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(email, password)
            server.send_message(msg)
            print("✅ Email sent successfully! Check your inbox and spam folder.")
            
    except Exception as e:
        print(f"❌ Failed to send email: {str(e)}")
        if "Application-specific password" in str(e):
            print("\nIMPORTANT: You must use an App Password, not your regular Gmail password")
            print("Generate one here: https://myaccount.google.com/apppasswords")

if __name__ == "__main__":
    send_final_test()