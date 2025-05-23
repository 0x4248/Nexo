from fastapi import FastAPI, Request, Header, HTTPException, UploadFile, File, Form, Response, APIRouter
from fastapi.responses import JSONResponse, PlainTextResponse, HTMLResponse, FileResponse
from typing import Annotated

import hashlib

from .. import database
from .. import utils
from .. import sessions_manager
from .. import responses
import os

router = APIRouter()

@router.get("/register")
async def register_page(request: Request):
    form = """
    <h2>Register</h2>
    <form method="post" action="/register">
        Username: <input name="username" required><br>
        Password: <input type="password" name="password" required><br>
        <input type="submit" value="Register">
    </form>
    """
    return HTMLResponse(utils.generate_html(request=request, title="Register", main_content=form))


@router.post("/register")
async def register_user(request: Request, username: str = Form(...), password: str = Form(...)):
    banned_usernames = ["admin", "administrator", "root", "system", "nexo_bot", "nexo", "owner", "moderator", "user", "guest", "anonymous"]
    banned_chars = [" ", "/", "\\", ":", "*", "?", "\"", "<", ">", "|", "!", "@", "#", "$", "%", "^", "&", "(", ")", "{", "}", "[", "]", ";", "'", ",", ".", "`", "~"]
    allowed_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
    if not all(char in allowed_chars for char in username):
        return responses.Account.Errors.username_invalid(request)
    
    min_length = 3
    max_length = 20

    if len(username) < min_length or len(username) > max_length:
        return responses.Account.Errors.username_length(request, min_length, max_length)
    if username in banned_usernames:
        return responses.Account.Errors.username_banned(request)
    if any(char in banned_chars for char in username):
        return responses.Account.Errors.username_invalid(request)
    if database.User.Check.exists(username):
        return responses.Account.Errors.username_exists(request)
    
    username = username.lower()
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    database.User.Core.create_user(username, hashed_pw, "member")
    database.User.Set.about_me(username, "This user has not set an about me yet.")
    
    return responses.Account.Success.user_created(request)

@router.get("/login")
async def login_page(request: Request):
    form = """
    <h2>Welcome to Nexo, please login</h2>
    <form method="post" action="/login">
        Username: <input name="username" required><br>
        Password: <input type="password" name="password" required><br>
        <input type="submit" value="Login">
    </form>
    """
    return HTMLResponse(utils.generate_html(request=request, title="Nexo Textboard | Login to your account", main_content=form))


@router.post("/login")
async def login_user(request: Request, response: Response, username: str = Form(...), password: str = Form(...)):
    user =  database.User.Core.get_user(username)
    if user and user['Banned'] == "True":
        reason = user['BanReason']
        return HTMLResponse(utils.generate_html(request=request, main_content="Your account is banned. You can appeal the ban by contacting the system administrator.\nReason: " + reason))
    if not user or user['Password'] != hashlib.sha256(password.encode()).hexdigest():
        return HTMLResponse(utils.generate_html(request=request, main_content="Invalid username or password. <a href='/login'>Try again</a> or <a href='/register'>register</a>."))

    session_id = sessions_manager.login_user(request, username)
    if not session_id:
        return HTMLResponse(utils.generate_html(request=request, main_content="Failed to create session. <a href='/login'>Try again</a> or <a href='/register'>register</a>."))
    response = HTMLResponse(utils.generate_html(request=request, main_content="Login successful! Redirecting to home... <script>setTimeout(function() { window.location.href = '/'; }, 2000);</script>"))
    response.set_cookie("session_id", session_id)
    return response

@router.get("/logout")
async def logout(request: Request, response: Response):

    user = sessions_manager.get_current_user(request)
    if not user:
        return HTMLResponse(utils.generate_html(request=request, main_content="You are not logged in. <a href='/login'>Login</a> or <a href='/register'>register</a>."))
    sessions_manager.logout_user(request)
    return HTMLResponse(utils.generate_html(request=request, main_content="Logout successful! Redirecting to home... <script>document.cookie = 'session_id=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;'; setTimeout(function() { window.location.href = '/'; }, 2000);</script>"))


@router.get("/account")
async def account_page(request: Request):
    user = sessions_manager.get_current_user(request)
    if not user:
        return HTMLResponse(utils.generate_html(request=request, main_content="You are not logged in. <a href='/login'>Login</a> or <a href='/register'>register</a>."))
    
    form = f"""
<h2>Account settings for {user}</h2>
<form method="post" action="/account/setpassword">
New password: <input type="password" name="password" required><br>
<input type="submit" value="Change password">
</form>
<form method="post" action="/account/setaboutme">
About me: <textarea name="aboutme" rows="4" cols="50" required placeholder="Tell us about yourself...(Markdown supported)"></textarea><br>
<input type="submit" value="Change about me">
</form>
<form method="post" action="/account/setprofilepic" enctype="multipart/form-data">
Profile picture: <input type="file" name="profilepic" accept="image/*" required><br>
<input type="submit" value="Change profile picture">
</form>
<form method="post" action="/account/delete">
<input type="submit" value="Delete account">
</form>
    """
    return HTMLResponse(utils.generate_html(request=request, title="Nexo Textboard | Account settings", main_content=form))
@router.post("/account/setpassword")
async def set_password(request: Request, password: str = Form(...)):
    user = sessions_manager.get_current_user(request)
    if not user:
        return HTMLResponse(utils.generate_html(request=request, main_content="You are not logged in. <a href='/login'>Login</a> or <a href='/register'>register</a>."))
    
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    database.User.Set.password(user, hashed_pw)
    return HTMLResponse(utils.generate_html(request=request, main_content="Password changed successfully!"))
@router.post("/account/setaboutme")
async def set_about_me(request: Request, aboutme: str = Form(...)):
    user = sessions_manager.get_current_user(request)
    if not user:
        return HTMLResponse(utils.generate_html(request=request, main_content="You are not logged in. <a href='/login'>Login</a> or <a href='/register'>register</a>."))

    database.User.Set.about_me(user, aboutme)
    return HTMLResponse(utils.generate_html(request=request, main_content="About me changed successfully!"))

@router.post("/account/setprofilepic")
async def set_profile_pic(request: Request, profilepic: UploadFile = File(...)):
    user = sessions_manager.get_current_user(request)
    if not user:
        return HTMLResponse(utils.generate_html(request=request, main_content="You are not logged in. <a href='/login'>Login</a> or <a href='/register'>register</a>."))
    
    if not profilepic.filename.endswith(('.png', '.jpg', '.jpeg', '.gif')):
        return HTMLResponse(utils.generate_html(request=request, main_content="Invalid file type. Only PNG files are allowed."))
    
    file_path = f"data/users/{user}/profile_pic.png"
    if os.path.exists(file_path):
        os.remove(file_path)
    if not os.path.exists(f"data/users/{user}/"):
        os.makedirs(f"data/users/{user}/")
    with open(file_path, "wb") as f:
        f.write(await profilepic.read())
    return HTMLResponse(utils.generate_html(request=request, main_content="Profile picture changed successfully!"))

@router.post("/account/delete")
async def delete_account(request: Request):
    user = sessions_manager.get_current_user(request)
    if not user:
        return HTMLResponse(utils.generate_html(request=request, main_content="You are not logged in. <a href='/login'>Login</a> or <a href='/register'>register</a>."))
    
    # database.User.delete_user(user)
    sessions_manager.logout_user(request)
    return HTMLResponse(utils.generate_html(request=request, main_content="Account deleted successfully!"))

@router.get("/account/{username}")
async def account_page(request: Request, username: str):
    if not database.User.Check.exists(username):
        return HTMLResponse(utils.generate_html(request=request, main_content="User does not exist. <a href='/login'>Login</a> or <a href='/register'>register</a>."))

    about_me = database.User.Get.about_me(username)
    role = utils.get_username_tag(username)
    page_content = f"""
<h2>Account page for {username} {role}</h2>
<img src="/account/{username}/profile_pic" alt="Profile picture" style="width: 100px; height: 100px;"><br>
<b>About me:</b>
{about_me}<br>
    """
    return HTMLResponse(utils.generate_html(request=request, title=f"Nexo Textboard | Account page for {username}", main_content=page_content))


@router.get("/account/{username}/profile_pic")
async def get_profile_pic(request: Request, username: str):
    if not database.User.Check.exists(username):
        return HTMLResponse(utils.generate_html(request=request, main_content="User does not exist. <a href='/login'>Login</a> or <a href='/register'>register</a>."))
    
    file_path = f"data/users/{username}/profile_pic.png"
    if not os.path.exists(file_path):
        return FileResponse("src/static/base.png")
    
    return FileResponse(file_path)

# TODO: theme