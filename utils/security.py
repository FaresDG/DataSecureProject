from flask import request
from models import db, AuthLog
from datetime import datetime

def log_auth_attempt(email, action, success, user_id=None, details=None):
    """Record an authentication attempt in the logs"""
    log = AuthLog(
        user_id=user_id,
        email=email,
        action=action,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent'),
        success=success,
        details=details
    )
    
    db.session.add(log)
    db.session.commit()

def get_client_ip():
    """Retrieve the client IP address accounting for proxies"""
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip = request.remote_addr
    return ip