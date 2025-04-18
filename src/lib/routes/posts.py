from fastapi import FastAPI, Request, Header, HTTPException, UploadFile, File, Form, Response, APIRouter
from fastapi.responses import JSONResponse, PlainTextResponse, HTMLResponse, FileResponse

from typing import Annotated
import hashlib
import datetime
from dateutil.relativedelta import relativedelta
from lib import database
from lib import meta_storage
from lib import utils
from lib import sessions_manager
from lib import topics

router = APIRouter()

ADMIN_TOPICS = ["/admin/", "/announcements/", "/news/", "/updates/", "/system/"]

@router.get("/new_post")
async def new_post_page(request: Request):
    user = sessions_manager.get_current_user(request)
    if not user:
        return HTMLResponse(utils.generate_html(request=request, main_content="You must be logged in to create a post. <a href='/login'>Login</a> or <a href='/register'>register</a>."))
    
    topics_list = topics.get_topics()
    topics_dropdown = "<select name=\"topic\">"
    for topic in topics_list:
        topics_dropdown += f"<option value=\"{topic}\">{topic}</option>"
    topics_dropdown += "</select>"
    
    
    main_content = f"""
<h2>Create a New Post</h2>
Make sure to follow the <a href="/docs/terms">Terms of Service</a> and <a href="/docs/privacy">Privacy Policy</a> when creating a post.<br>
All XSS attacks will be blocked but tags like b, i, u, a are allowed.<br>
<form action="/submit_post" method="post">
<input type="hidden" name="author" value="{user}">
Title: <input type="text" name="title" required><br>
Topics: {topics_dropdown}
Content:<br>
<textarea name="content" rows="10" cols="50" required></textarea><br>
<input type="submit" value="Create Post">
</form>
    """
    return HTMLResponse(utils.generate_html(request=request, title="Nexo Textboard | Create a new post", main_content=main_content))



@router.post("/submit_post")
async def submit_post(
    request: Request,
    title: str = Form(...),
    author: str = Form(...),
    topic: str = Form(...),
    content: str = Form(...)
):
    id = hashlib.sha256((title + author + topic + content).encode()).hexdigest()
    id = id[:10]
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    database.PublicPosts.add_post(id, title, author, timestamp, topic)
    meta_storage.PublicPosts.add_post(id, title, author, timestamp, topic, content)

    return HTMLResponse(utils.generate_html(
        request=request,
        title="Post Created",
        main_content=f"<p>Post created successfully!</p><a href=\"/post/{id}\">View your post</a>",
        footer_content="Post submission successful"
    ))



@router.get("/posts")
async def posts(request: Request, page: int = 0):
    posts = database.PublicPosts.get_post_by_page(page)
    main_content = "<a href=\"/\">Home</a> > <a href=\"/posts\">Public posts</a><br>"
    for post in posts:
        # want it like 2d ago, 1h ago, 1m ago, 1y ago
        relative_time = ""
        post_time = datetime.datetime.strptime(post[3], "%Y-%m-%d %H:%M:%S")
        now = datetime.datetime.now()
        diff = relativedelta(now, post_time)
        if diff.years > 0:
            relative_time = f"{diff.years}y ago"
        elif diff.months > 0:
            relative_time = f"{diff.months}m ago"
        elif diff.days > 0:
            relative_time = f"{diff.days}d ago"
        elif diff.hours > 0:
            relative_time = f"{diff.hours}h ago"
        elif diff.minutes > 0:
            relative_time = f"{diff.minutes}m ago"
        elif diff.seconds > 0:
            relative_time = f"{diff.seconds}s ago"
        else:
            relative_time = "Just now"
        main_content += f"{relative_time} Posted in <b>{post[4]}</b> by <i>{post[2]}</i> {utils.get_username_tag(post[2])}\n <a href=\"/post/{post[0]}\">{post[1]}</a>\n\n"
    if not posts:
        main_content = "No posts found<br>"
    if page < 0:
        main_content += "<a href=\"/posts?page=" + str(page - 1) + "\"><-</a> "
    else:
        main_content += "<a href=\"/posts?page=" + str(page - 1) + "\"><-</a> Page " + str(page) + " <a href=\"/posts?page=" + str(page + 1) + "\">-></a>"
    footer_content = "200 OK"
    return HTMLResponse(utils.generate_html(request=request, title="Nexo Textboard | Public posts", main_content=main_content, footer_content=footer_content))


@router.post("/create_post")
async def create_post(request: Request, title: Annotated[str, Header()], author: Annotated[str, Header()], topic: Annotated[str, Header()], content: Annotated[str, Header()]):
    id = hashlib.sha256((title + author + topic + content).encode()).hexdigest()
    id = id[:10]
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    database.PublicPosts.add_post(id, title, author, timestamp, topic)
    meta_storage.PublicPosts.add_post(id, title, author, timestamp, topic, content)
    return JSONResponse(content={"status": "success", "id": id})

@router.get("/post/{id}")
async def get_post(request: Request, id: str):

    post = meta_storage.PublicPosts.get_post(id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    main_content = "<a href=\"/\">Home</a> > <a href=\"/posts\">Public posts</a> > <a href=\"/post/" + id + "\">" + post['title'] + "</a><br><br>"
    main_content += f"<b>{post['title']}</b><br>"
    main_content += f"<b>AUTHOR: </b><i>{post['author']}</i> <b>{post['timestamp']}</b><br>"
    main_content += f"<b>TOPIC:</b> {post['topic']}<br><br>"
    main_content += f"{post['content']}<br>"
    main_content += "<hr>"
    main_content += "<b>--REPLIES--</b><br>"
    if not post['replies'] or len(post['replies']) == 0:
        main_content += "No replies found<br>"
    for reply in post['replies']:
        main_content += f"<b>REPLY:</b> <i>{reply['username']}</i> <b>{reply['timestamp']}</b><br>"
        main_content += f"{reply['content']}<br>"
    
    user = sessions_manager.get_current_user(request)
    if user:
        main_content += "<hr>"
        main_content += "<h2>Reply to this post</h2>"
        main_content += f"<form action=\"/reply/{id}\" method=\"post\">"
        main_content += f"<input type=\"textarea\" name=\"content\" rows=\"10\" cols=\"50\" required></textarea><br>"
        main_content += f"<input type=\"submit\" value=\"Reply\">"
        main_content += "</form>"
    else:
        main_content += "<hr>"
        main_content += "<h2>Reply to this post</h2>"
        main_content += "You must be logged in to reply to a post. <a href='/login'>Login</a> or <a href='/register'>register</a>."
    return HTMLResponse(utils.generate_html(request=request, title="Nexo Textboard | View post", main_content=main_content))

@router.post("/reply/{id}")
async def reply_post(request: Request, id: str, content: str = Form(...)):
    username = sessions_manager.get_current_user(request)
    
    if not username:
        return HTMLResponse(utils.generate_html(request=request, main_content="You must be logged in to reply to a post. <a href='/login'>Login</a> or <a href='/register'>register</a>."))
    if not content:
        return HTMLResponse(utils.generate_html(request=request, main_content="Content cannot be empty. <a href='/posts'>Go back</a>"))    
    if not meta_storage.PublicPosts.get_post(id):
        raise HTTPException(status_code=404, detail="Post not found")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    meta_storage.PublicPosts.add_reply(id, username, content, timestamp)
    return HTMLResponse(utils.generate_html(request=request, title="Reply submitted", main_content="Reply submitted successfully! Redirecting to post... <script>setTimeout(function() { window.location.href = '/post/" + id + "'; }, 1000);</script>"))
