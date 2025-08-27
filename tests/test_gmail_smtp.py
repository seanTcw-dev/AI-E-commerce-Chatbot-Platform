import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

def test_gmail_smtp():
    """Test Gmail SMTP authentication and email sending"""
    
    # Load environment variables with absolute path
    dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    print(f"--- Loading .env file from: {dotenv_path} ---")
    load_dotenv(dotenv_path=dotenv_path)
    
    # Get credentials
    sender_email = os.environ.get("GMAIL_SENDER_EMAIL")
    password = os.environ.get("GMAIL_APP_PASSWORD")
    
    print("--- Testing Gmail SMTP Credentials ---")
    print(f"Email: {sender_email}")
    print(f"App Password: {'*' * len(password) if password else '(Not Found)'}")
    print("-" * 50)
    
    if not sender_email or not password:
        print("[ERROR] Missing credentials in .env file")
        return False
    
    # Test SMTP login
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            print("[INFO] Connecting to Gmail SMTP server...")
            server.login(sender_email, password)
            print("[OK] SMTP Login successful!")
            
            # Test sending a simple email to yourself
            print("[INFO] Testing email sending...")
            
            message = MIMEMultipart()
            message["From"] = sender_email
            message["To"] = sender_email  # Send to yourself for testing
            message["Subject"] = "SMTP Test - Success!"
            
            body = "This is a test email to confirm SMTP is working correctly."
            message.attach(MIMEText(body, "plain"))
            
            server.sendmail(sender_email, sender_email, message.as_string())
            print("[OK] Test email sent successfully!")
            print(f"[INFO] Check your inbox: {sender_email}")
            
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"[ERROR] SMTP Authentication Failed: {e}")
        print("[HELP] Possible solutions:")
        print("   1. Check your email address is correct")
        print("   2. Regenerate your Google App Password")
        print("   3. Make sure 2FA is enabled on your Google account")
        return False
        
    except Exception as e:
        print(f"[ERROR] Unexpected error: {type(e).__name__} - {e}")
        return False

if __name__ == "__main__":
    success = test_gmail_smtp()
    if success:
        print("\n[SUCCESS] Gmail SMTP test completed successfully!")
        print("[OK] Your email configuration is ready for the main app.")
    else:
        print("\n[FAILED] Gmail SMTP test failed!")
        print("[ERROR] Please fix the issues above before running the main app.")
