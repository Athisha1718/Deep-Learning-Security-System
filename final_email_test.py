import smtplib, os
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

creds = {
    'email': os.getenv('EMAIL_USERNAME'),
    'pwd': os.getenv('GMAIL_APP_PASSWORD'),
    'server': 'smtp.gmail.com'
}

def forensic_check():
    assert len(creds['pwd']) == 16, "Password must be 16 chars"
    assert creds['pwd'].isalnum(), "Password contains illegal chars"
    print("🔬 Forensic check passed")

def send_email():
    try:
        msg = MIMEText("Final verification email")
        msg['Subject'] = 'URGENT: Flask Test'
        msg['From'] = creds['email']
        msg['To'] = creds['email']

        with smtplib.SMTP_SSL(creds['server'], 465) as s:
            s.login(creds['email'], creds['pwd'])
            s.send_message(msg)
            print("💣 Email detonated successfully!")

    except Exception as e:
        print(f"☢️ Critical failure: {e}")
        if "534" in str(e):
            print("""
            Google's nuclear authentication failsafe triggered.
            Possible causes:
            1. Account has login restrictions (check https://myaccount.google.com/security)
            2. Password was regenerated during this test
            3. Google blocked your IP (try mobile hotspot)
            """)

forensic_check()
send_email()