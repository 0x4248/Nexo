from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from lib import database, meta_storage, utils, sessions_manager
import hashlib
import datetime

router = APIRouter()

ADMIN_ROLES = ["owner", "admin", "moderator"]

def is_admin(user: str) -> bool:
    role = database.User.get_role(user)
    return role in ADMIN_ROLES


@router.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request):
    user = sessions_manager.get_current_user(request)
    if not user or not is_admin(user):
        return HTMLResponse(utils.generate_html(request=request, main_content="You are not authorized to view this page."))

    form = f"""
    <h2>Admin Panel - Welcome, {user}</h2>

    <form method="post" action="/admin/deletepost">
        <h3>Delete Post</h3>
        Post ID: <input type="text" name="post_id" required><br>
        <input type="submit" value="Delete Post">
    </form>

    <form method="post" action="/admin/banuser">
        <h3>Ban User</h3>
        Username: <input type="text" name="ban_username" required><br>
        <input type="submit" value="Ban User">
    </form>

    <form method="post" action="/admin/createtopic">
        <h3>Create Topic</h3>
        Topic Name: <input type="text" name="topic" required><br>
        <input type="submit" value="Create Topic">
    </form>

    <form method="post" action="/admin/systempost">
        <h3>Post as SYSTEM</h3>
        Title: <input type="text" name="title" required><br>
        Topic: <input type="text" name="topic" required><br>
        Content: <br><textarea name="content" rows="5" cols="40" required></textarea><br>
        <input type="submit" value="Post">
    </form>
    """
    return HTMLResponse(utils.generate_html(request=request, title="Admin Panel", main_content=form))


@router.post("/admin/deletepost")
async def delete_post(request: Request, post_id: str = Form(...)):
    user = sessions_manager.get_current_user(request)
    if not user or not is_admin(user):
        return HTMLResponse(utils.generate_html(request=request, main_content="Unauthorized"))
    
    database.PublicPosts.delete_post(post_id)
    return RedirectResponse(url="/admin", status_code=303)


@router.post("/admin/banuser")
async def ban_user(request: Request, ban_username: str = Form(...)):
    user = sessions_manager.get_current_user(request)
    if not user or not is_admin(user):
        return HTMLResponse(utils.generate_html(request=request, main_content="Unauthorized"))

    database.User.set_role(ban_username, "banned")
    return RedirectResponse(url="/admin", status_code=303)


@router.post("/admin/createtopic")
async def create_topic(request: Request, topic: str = Form(...)):
    user = sessions_manager.get_current_user(request)
    if not user or not is_admin(user):
        return HTMLResponse(utils.generate_html(request=request, main_content="Unauthorized"))

    meta_storage.Topics.add_topic(topic)
    return RedirectResponse(url="/admin", status_code=303)


@router.post("/admin/systempost")
async def system_post(request: Request, title: str = Form(...), topic: str = Form(...), content: str = Form(...)):
    user = sessions_manager.get_current_user(request)
    if not user or not is_admin(user):
        return HTMLResponse(utils.generate_html(request=request, main_content="Unauthorized"))

    id = hashlib.sha256((title + datetime.datetime.now().isoformat()).encode()).hexdigest()[:10]
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    database.PublicPosts.add_post(id, title, "nexo_bot", timestamp, topic)
    meta_storage.PublicPosts.add_post(id, title, "nexo_bot", timestamp, topic, content)
    return RedirectResponse(url="/admin", status_code=303)
