"""
Authentication and Session Management
Handles user authentication and session tracking
"""

import time
import logging

# Enhanced active sessions tracking
ACTIVE_SESSIONS = {}  # username -> {login_time, last_activity, session_id}

def update_user_activity(username):
    """Update user's last activity timestamp"""
    if username in ACTIVE_SESSIONS:
        ACTIVE_SESSIONS[username]["last_activity"] = time.time()

def cleanup_inactive_sessions():
    """Remove inactive sessions (older than 24 hours)"""
    current_time = time.time()
    inactive_users = []
    for username, session in ACTIVE_SESSIONS.items():
        if current_time - session.get("last_activity", 0) > 86400:  # 24 hours
            inactive_users.append(username)
    
    for username in inactive_users:
        del ACTIVE_SESSIONS[username]
    
    if inactive_users:
        logging.info(f"Cleaned up {len(inactive_users)} inactive sessions")
