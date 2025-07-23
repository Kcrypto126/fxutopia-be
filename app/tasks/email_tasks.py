from celery import current_task
from app.core.celery_app import celery_app
from app.services.email_service import EmailService

@celery_app.task(bind=True)
def send_verification_email_task(self, email: str, token: str):
    """Background task to send verification email"""
    try:
        email_service = EmailService()
        result = email_service.send_verification_email(email, token)
        return {"status": "success", "email": email}
    except Exception as exc:
        # Retry failed task
        raise self.retry(exc=exc, countdown=60, max_retries=3)

@celery_app.task(bind=True)
def send_password_reset_email_task(self, email: str, token: str):
    """Background task to send password reset email"""
    try:
        email_service = EmailService()
        result = email_service.send_password_reset_email(email, token)
        return {"status": "success", "email": email}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60, max_retries=3)

@celery_app.task
def cleanup_expired_sessions():
    """Clean up expired user sessions"""
    from datetime import datetime
    from app.database import SessionLocal
    from app.models.user import UserSession
    
    db = SessionLocal()
    try:
        expired_sessions = db.query(UserSession).filter(
            UserSession.expires_at < datetime.utcnow()
        ).all()
        
        for session in expired_sessions:
            db.delete(session)
        
        db.commit()
        return {"cleaned_sessions": len(expired_sessions)}
    finally:
        db.close()
