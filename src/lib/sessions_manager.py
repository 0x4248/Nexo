import secrets

import lib.logger as logger

sessions = {}

def get_current_user(request):
    session_id = request.cookies.get("session_id")
    logger.log("SessionManager", f"Get current user request: {request}")
    
    return sessions.get(session_id)

def login_user(request, username):
    session_id = request.cookies.get("session_id")
    if session_id:
        sessions[session_id] = username
    else:
        session_id = secrets.token_hex(16)
        sessions[session_id] = username
    logger.log("SessionManager", f"User {username} logged in.")
    return session_id

def logout_user(request):
    session_id = request.cookies.get("session_id")
    if session_id in sessions:
        del sessions[session_id]
        logger.log("SessionManager", f"User {sessions[session_id]} logged out.")
    else:
        logger.log("SessionManager", "Logout request with no session ID.")
    return session_id

def is_logged_in(request):
    session_id = request.cookies.get("session_id")
    logger.log("SessionManager", f"Check if user is logged in: {request}")
    return session_id in sessions

def get_user_role(request):
    session_id = request.cookies.get("session_id")
    if session_id in sessions:
        return sessions[session_id]
    return None