
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
from typing import List
from app.config import get_settings

settings = get_settings()

class EmailService:
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.EMAILS_FROM_EMAIL
        self.from_name = settings.EMAILS_FROM_NAME
        
        # Initialize Jinja2 environment for email templates
        self.jinja_env = Environment(
            loader=FileSystemLoader("app/templates/emails")
        )
    
    def send_email(
        self,
        subject: str,
        recipients: List[str],
        html_content: str,
        text_content: str = None
    ):
        """Send email"""
        if not self.smtp_host:
            return False
        
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{self.from_name} <{self.from_email}>"
        msg["To"] = ", ".join(recipients)
        
        if text_content:
            part1 = MIMEText(text_content, "plain")
            msg.attach(part1)
        
        part2 = MIMEText(html_content, "html")
        msg.attach(part2)
        
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if settings.SMTP_TLS:
                    server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
    
    def send_verification_email(self, email: str, token: str):
        """Send email verification"""
        template = self.jinja_env.get_template("verification.html")
        html_content = template.render(
            verification_link=f"https://yourdomain.com/verify-email?token={token}"
        )
        
        return self.send_email(
            subject="Verify Your Email - FxUtopia",
            recipients=[email],
            html_content=html_content
        )
    
    def send_password_reset_email(self, email: str, token: str):
        """Send password reset email"""
        template = self.jinja_env.get_template("password_reset.html")
        html_content = template.render(
            reset_link=f"https://yourdomain.com/reset-password?token={token}"
        )
        
        return self.send_email(
            subject="Reset Your Password - FxUtopia",
            recipients=[email],
            html_content=html_content
        )