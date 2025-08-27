import os
import smtplib
import ssl
import uuid
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import pandas as pd

def test_new_email_format():
    """Test the new email format"""
    
    # Load environment variables
    dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    load_dotenv(dotenv_path=dotenv_path)
    
    sender_email = os.environ.get("GMAIL_SENDER_EMAIL")
    password = os.environ.get("GMAIL_APP_PASSWORD")
    
    if not sender_email or not password:
        print("❌ Credentials not found!")
        return False
    
    # Generate test data
    session_id = str(uuid.uuid4())
    chat_link = f"http://localhost:5000/agent-chat/{session_id}"
    
    print("🧪 Testing New Email Format...")
    print(f"📧 Sending to: {sender_email}")
    print(f"🔗 Chat link: {chat_link}")
    print(f"🆔 Session ID: {session_id}")
    
    # Create email with new format
    message = MIMEMultipart("alternative")
    message["Subject"] = "🌟 New Live Chat Request - Test"
    message["From"] = sender_email
    message["To"] = sender_email  # Send to yourself for testing
    
    # Plain text version
    text = f"""\
Hi there!

A customer has requested a live chat session and needs your assistance.

Session Details:
- Session ID: {session_id}
- Time: {str(pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'))}

To join the chat, please click this link:
{chat_link}

Thank you for your prompt response!

Best regards,
Sephora Customer Support System
    """
    
    # HTML version with full styling
    html = f"""\
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>New Live Chat Request</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f9f9f9;
        }}
        .container {{
            background-color: #ffffff;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        .header {{
            text-align: center;
            border-bottom: 3px solid #d63384;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: #d63384;
            margin: 0;
            font-size: 28px;
        }}
        .content {{
            margin-bottom: 30px;
        }}
        .session-info {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid #d63384;
        }}
        .session-info h3 {{
            margin-top: 0;
            color: #d63384;
        }}
        .session-info p {{
            margin: 8px 0;
            font-weight: 500;
        }}
        .cta-button {{
            display: inline-block;
            background-color: #d63384;
            color: #ffffff;
            text-decoration: none;
            padding: 15px 30px;
            border-radius: 25px;
            font-weight: bold;
            font-size: 16px;
            text-align: center;
            margin: 20px 0;
            transition: background-color 0.3s ease;
        }}
        .cta-button:hover {{
            background-color: #b02a5b;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #666;
            font-size: 14px;
        }}
        .urgent {{
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .urgent strong {{
            color: #856404;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌟 New Live Chat Request</h1>
        </div>
        
        <div class="content">
            <div class="urgent">
                <strong>⏰ Urgent:</strong> A customer is waiting for live assistance!
            </div>
            
            <p>Hello,</p>
            <p>A customer has requested a live chat session and needs your immediate assistance. Please join the chat as soon as possible to provide excellent customer service.</p>
            
            <div class="session-info">
                <h3>📋 Session Details</h3>
                <p><strong>Session ID:</strong> {session_id}</p>
                <p><strong>Time:</strong> {str(pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'))}</p>
                <p><strong>Status:</strong> Waiting for Agent</p>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{chat_link}" class="cta-button">
                    💬 Join Chat Now
                </a>
            </div>
            
            <p><strong>Direct Link:</strong> <a href="{chat_link}" style="color: #d63384;">{chat_link}</a></p>
            
            <p>Thank you for your prompt response and excellent customer service!</p>
        </div>
        
        <div class="footer">
            <p>This is an automated message from the Sephora Customer Support System</p>
            <p>Please do not reply to this email</p>
        </div>
    </div>
</body>
</html>
    """
    
    # Create MIME parts
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    
    message.attach(part1)
    message.attach(part2)
    
    # Send email
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, sender_email, message.as_string())
        print("✅ Test email sent successfully!")
        print("📧 Check your inbox for the improved email format")
        return True
    except Exception as e:
        print(f"❌ Error sending test email: {e}")
        return False

if __name__ == "__main__":
    test_new_email_format()
