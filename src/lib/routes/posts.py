from fastapi import FastAPI, Request, Header, HTTPException, UploadFile, File, Form, Response, APIRouter
from fastapi.responses import JSONResponse, PlainTextResponse, HTMLResponse, FileResponse

from typing import Annotated
import hashlib
import datetime
from dateutil.relativedelta import relativedelta
from .. import database
from .. import utils
from .. import sessions_manager

router = APIRouter()

ADMIN_TOPICS = ["/admin/", "/announcements/", "/news/", "/updates/", "/system/"]

@router.get("/new_post")
async def new_post_page(request: Request):
    user = sessions_manager.get_current_user(request)
    if not user:
        return HTMLResponse(utils.generate_html(request=request, main_content="You must be logged in to create a post. <a href='/login'>Login</a> or <a href='/register'>register</a>."))
    
    topics_list = database.Topics.Core.get_all_topics()
    topics_dropdown = "<select name=\"topic\">"
    for topic in topics_list:
        topics_dropdown += f"<option value=\"{topic['ID']}\">{topic['ID']}</option>"
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
    # TODO: Add validation for /topic/
    id = hashlib.sha256((title + author + topic + content).encode()).hexdigest()
    id = id[:10]
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    database.PublicPosts.Core.add_post(
        id=id,
        title=title,
        author=author,
        timestamp=timestamp,
        topic=topic,
        body=content
    )
    return HTMLResponse(utils.generate_html(
        request=request,
        title="Post Created",
        main_content=f"<p>Post created successfully!</p><a href=\"/post/{id}\">View your post</a>",
        footer_content="Post submission successful"
    ))



@router.get("/posts")
async def posts(request: Request, page: int = 0):
    if page < 0:
        return HTMLResponse(utils.generate_html(request=request, title="Nexo Textboard | Public posts", main_content="Why are you doing a negative page lmao?\nYou know thats not how databases work right?"))
    posts = database.PublicPosts.Core.get_post_by_page(page)
    main_content = "<a href=\"/\">Home</a> > <a href=\"/posts\">Public posts</a><br>"
    for post in posts:
        relative_time = ""
        post_time = datetime.datetime.strptime(post['Timestamp'], "%Y-%m-%d %H:%M:%S")
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
        main_content += f"{relative_time} Posted in <b>{post['Topic']}</b> by <i>{post['Author']}</i> {utils.get_username_tag(post['Author'])}\n <a href=\"/post/{post['ID']}\">{post['Title']}</a>\n\n"
    if not posts:
        main_content = "No posts found<br>"
    if page == 0:
        main_content += "<- Page 0 <a href=\"/posts?page=" + str(page + 1) + "\">-></a>"
    else:
        main_content += "<a href=\"/posts?page=" + str(page - 1) + "\"><-</a> Page " + str(page) + " <a href=\"/posts?page=" + str(page + 1) + "\">-></a>"
    footer_content = "200 OK"
    return HTMLResponse(utils.generate_html(request=request, title="Nexo Textboard | Public posts", main_content=main_content, footer_content=footer_content))

@router.get("/post/{id}")
async def get_post(request: Request, id: str):
    logged_in_user = sessions_manager.get_current_user(request)
    is_admin = database.User.Check.is_admin(logged_in_user) if logged_in_user else False
    post = database.PublicPosts.Core.get_post(id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    main_content = f"<h2>{post['Title']}</h2>"
    main_content += f"<b>AUTHOR: </b><i><a href=\"/account/{post['Author']}\">{post['Author']}</a></i> <b>{post['Timestamp']}</b><br>"
    main_content += f"<b>TOPIC:</b> <a href=\"/topic{post['Topic']}\">{post['Topic']}</a><br>"
    main_content += f"{post['Body']}<br>"
    main_content += "<hr>"
    main_content += "<b>----REPLIES----</b><br><br>"
    if post['Replies'] == "":
        main_content += "No replies yet<br>"
    post['Replies'] = post['Replies'].split(",")
    for reply in post['Replies']:
        if reply == "":
            continue
        reply_data = database.PublicPostReplies.Core.get_reply(reply)
        if not reply_data:
            continue
        main_content += f"<section id=\"reply_{reply_data['ID']}\">"
        main_content += f"<b>REPLY:</b> <i><a href=\"/account/{reply_data['Author']}\">{reply_data['Author']}</a></i> <b>{reply_data['Timestamp']}</b> <i>{reply_data['ID']}</i><br>"
        main_content += f"{reply_data['Body']}<br>"
        main_content += "</section>"
        
    user = sessions_manager.get_current_user(request)
    main_content += "<section id=\"reply_section\">"
    if user:
        main_content += "<h2>Reply to this post</h2>"
        main_content += f"<b>Logged in as: {user}</b><br>"
        main_content += f"<form action=\"/reply/{id}\" method=\"post\">"
        main_content += f"<textarea name=\"content\" id=\"reply_box\" rows=\"10\" cols=\"50\" required></textarea><br>"
        main_content += f"<input type=\"submit\" value=\"Reply\">"
        main_content += "</form>"
    else:
        main_content += "<h2>Reply to this post</h2>"
        main_content += "You must be logged in to reply to a post. <a href='/login'>Login</a> or <a href='/register'>register</a>."
    main_content += "</section>"
    if is_admin:
        main_content += "<hr>"
        main_content += "<h2>Admin actions</h2>"
        main_content += f"[<a onclick=\"document.getElementById('admin_actions').style.display = 'block';\">Show admin actions</a>]<br>"
        main_content += "<div id=\"admin_actions\" style=\"display: none;\">"
        main_content += f"[<a href=\"/admin/deletepost/{id}\">Delete post</a>] "
        main_content += f"[<a href=\"/admin/banuser/{post['Author']}\">Ban user</a>]<br>"
        main_content += f"</div>"
        main_content += "<script>"
        main_content += "function replyQuote(id) {"
        main_content += "document.getElementById('reply_box').value = document.getElementById('reply_' + id).innerText;"
    return HTMLResponse(utils.generate_html(request=request, title="Nexo Textboard | View post", main_content=main_content))

@router.post("/reply/{id}")
async def reply_post(request: Request, id: str, content: str = Form(...)):
    username = sessions_manager.get_current_user(request)
    
    if not username:
        return HTMLResponse(utils.generate_html(request=request, main_content="You must be logged in to reply to a post. <a href='/login'>Login</a> or <a href='/register'>register</a>."))
    if not content:
        return HTMLResponse(utils.generate_html(request=request, main_content="Content cannot be empty. <a href='/posts'>Go back</a>"))    
    if not database.PublicPosts.Core.get_post(id):
        raise HTTPException(status_code=404, detail="Post not found")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    reply_id = hashlib.sha256((content + username + id).encode()).hexdigest()
    reply_id = reply_id[:10]
    database.PublicPostReplies.Core.add_reply(reply_id=reply_id, post_id=id, author=username, body=content, timestamp=timestamp)

    return HTMLResponse(utils.generate_html(request=request, title="Reply submitted", main_content="Reply submitted successfully! Redirecting to post... <script>setTimeout(function() { window.location.href = '/post/" + id + "'; }, 1000);</script>"))


@router.get("/topics")
async def topic(request: Request):
    topics_list = database.Topics.Core.get_all_topics()
    main_content = "<a href=\"/\">Home</a> > <a href=\"/posts\">Public posts</a> > <a href=\"/topic\">Topics</a><br>"
    main_content += "<h2>Topics</h2>"
    main_content += "<ul>"
    for topic in topics_list:
        name = topic['ID']
        name.replace("/", "")
        if topic['AdminOnly'] == 'True':
            main_content += f"<li><a href=\"/topic{name}\">{name}</a> - {topic['Description']} <span class=\"admin_role\">ADMIN TOPIC</span></li>"
        else:
            main_content += f"<li><a href=\"/topic{name}\">{name}</a> - {topic['Description']}</li>"
    main_content += "</ul>"
    return HTMLResponse(utils.generate_html(request=request, title="Nexo Textboard | Topics", main_content=main_content))

@router.get("/topic/{topic_name}")
async def topic_posts(request: Request, topic_name: str, page: int = 0):
    topic_name = "/"+topic_name+"/"
    posts = database.PublicPosts.Core.get_posts_by_topic(topic_name, page)
    topic_info = database.Topics.Core.get_topic(topic_name)
    description = topic_info['Description'] if topic_info else "No description available"
    main_content = f"<b>{topic_name}</b><br>"
    main_content += f"{description}<br><br>"
    main_content += "All posts ordered by timestamp<br>"

    for post in posts:
        relative_time = ""
        post_time = datetime.datetime.strptime(post['Timestamp'], "%Y-%m-%d %H:%M:%S")
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
        main_content += f"{relative_time} Posted in <b>{post['Topic']}</b> by <i>{post['Author']}</i> {utils.get_username_tag(post['Author'])}\n <a href=\"/post/{post['ID']}\">{post['Title']}</a>\n\n"
    if page == 0:
        main_content += "<- Page 0 <a href=\"/topic/" + topic_name + "?page=" + str(page + 1) + "\">-></a>"
    else:
        main_content += "<a href=\"/topic/" + topic_name + "?page=" + str(page - 1) + "\"><-</a> Page " + str(page) + " <a href=\"/topic/" + topic_name + "?page=" + str(page + 1) + "\">-></a>"


    if not posts:
        main_content = "No posts found<br>"
    return HTMLResponse(utils.generate_html(request=request, title="Nexo Textboard | Topic", main_content=main_content))