"""
Email Service Module for handling email notifications to agents
"""
import os
import smtplib
import ssl
import pandas as pd
from flask import render_template
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailService:
    def __init__(self):
        self.sender_email = os.environ.get("GMAIL_SENDER_EMAIL")
        self.password = os.environ.get("GMAIL_APP_PASSWORD")
        self.agent_emails = []
        self.load_agent_emails()
    
    def load_agent_emails(self):
        """Load the list of agent emails from the agents.txt file"""
        # First check if the path was set by app.py
        agents_file_path = os.environ.get('AGENTS_FILE_PATH')
        
        if agents_file_path and os.path.exists(agents_file_path):
            try:
                with open(agents_file_path, 'r') as f:
                    self.agent_emails = [line.strip() for line in f if line.strip()]
                print(f"[OK] Loaded {len(self.agent_emails)} agent emails from {agents_file_path}")
                return
            except Exception as e:
                print(f"[ERROR] Failed to read agents file at {agents_file_path}: {e}")
        
        # Fallback: Try multiple possible locations for agents.txt
        possible_paths = [
            'agents.txt',  # Current directory
            os.path.join('..', 'agents.txt'),  # Parent directory
            os.path.join('..', '..', 'agents.txt'),  # Grandparent directory
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'agents.txt')  # Absolute path
        ]
        
        agents_file_found = False
        for path in possible_paths:
            try:
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        self.agent_emails = [line.strip() for line in f if line.strip()]
                    print(f"[OK] Loaded {len(self.agent_emails)} agent emails from {path}")
                    agents_file_found = True
                    break
            except Exception as e:
                continue
        
        if not agents_file_found:
            print("[WARNING] agents.txt file not found. No agents will be notified.")
            self.agent_emails = []

    def send_agent_notification(self, session_id, host_url):
        """Send notification email to all agents about new chat request"""
        if not self.sender_email or not self.password:
            print("⚠️ Gmail credentials not found in environment variables.")
            return False, "Email configuration error"

        if not self.agent_emails:
            print("⚠️ No agent emails available to send notification.")
            return False, "No agent emails configured"

        chat_link = host_url + f'agent-chat/{session_id}'
        timestamp = str(pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'))

        # Track results for all agents
        sent_count = 0
        failed_count = 0
        errors = []        # Prepare email templates once
        # Read and render plain text template
        try:
            # Get the absolute path to the templates directory
            current_dir = os.path.dirname(__file__)  # services directory
            chatbot_dir = os.path.dirname(current_dir)  # chatbot directory
            templates_dir = os.path.join(chatbot_dir, 'templates')
            
            # Try multiple possible locations for the template
            template_paths = [
                os.path.join(templates_dir, 'agent_notification_email.txt'),
                os.path.join(chatbot_dir, 'templates', 'agent_notification_email.txt'),
                os.path.join('templates', 'agent_notification_email.txt'),
                os.path.join('..', 'templates', 'agent_notification_email.txt'),
                os.path.join('..', '..', 'templates', 'agent_notification_email.txt')
            ]
            
            text_template = None
            for template_path in template_paths:
                if os.path.exists(template_path):
                    with open(template_path, 'r', encoding='utf-8') as f:
                        text_template = f.read()
                    print(f"[OK] Loaded text template from: {template_path}")
                    break
            
            if text_template is None:
                raise FileNotFoundError("Could not find agent_notification_email.txt template")
                
            # Simple string formatting instead of render_template_string
            text_content = text_template.format(
                session_id=session_id,
                timestamp=timestamp,
                chat_link=chat_link
            )
        except Exception as e:
            print(f"[ERROR] Error loading text email template: {e}")
            return False, "Email template error"

        # Render HTML template
        try:
            html_content = render_template('agent_notification_email.html', 
                                         session_id=session_id, 
                                         timestamp=timestamp, 
                                         chat_link=chat_link)
        except Exception as e:
            print(f"Error loading HTML email template: {e}")
            return False, "Email template error"

        # Send notification to all agents
        for agent_email in self.agent_emails:
            try:
                message = MIMEMultipart("alternative")
                message["Subject"] = "New Live Chat Request"
                message["From"] = self.sender_email
                message["To"] = agent_email

                # Turn these into plain/html MIMEText objects
                part1 = MIMEText(text_content, "plain")
                part2 = MIMEText(html_content, "html")

                # Add HTML/plain-text parts to MIMEMultipart message
                message.attach(part1)
                message.attach(part2)

                # Create secure connection with server and send email
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                    server.login(self.sender_email, self.password)
                    server.sendmail(self.sender_email, agent_email, message.as_string())
                
                print(f"Successfully sent chat request email to {agent_email}")
                sent_count += 1
                
            except smtplib.SMTPAuthenticationError as e:
                error_msg = f"SMTP authentication error for {agent_email}: {e}"
                print(f"!!! {error_msg}")
                errors.append(error_msg)
                failed_count += 1
            except Exception as e:
                error_msg = f"Email sending error for {agent_email}: {type(e).__name__} - {e}"
                print(f"!!! {error_msg}")
                errors.append(error_msg)
                failed_count += 1

        # Return results summary
        if sent_count > 0:
            success_msg = f"Successfully sent emails to {sent_count}/{len(self.agent_emails)} agents"
            if failed_count > 0:
                success_msg += f". {failed_count} failed: {'; '.join(errors)}"
            print(success_msg)
            return True, success_msg
        else:
            error_msg = f"Failed to send emails to all {len(self.agent_emails)} agents: {'; '.join(errors)}"
            print(error_msg)
            return False, error_msg
