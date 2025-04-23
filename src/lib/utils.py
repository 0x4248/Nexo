from fastapi import Request, Form
from datetime import datetime
from lib import sessions_manager
from lib import database
from lib import globals

def generate_html(request: Request, title="Nexo Textboard", main_content="Server did not return any content", footer_content=""):
    account_links = get_account_links(request)
    banner = open("src/static/banner.html", "r").read()
    return f"""
<!DOCTYPE html>
<html>
	<head>
		<meta charset="utf-8">
		<meta http-equiv="X-UA-Compatible" content="IE=edge">
		<title>{title}</title>
		<meta name="description" content="">
		<meta name="viewport" content="width=device-width, initial-scale=1">
		<link rel="stylesheet" href="/style">
	</head>
	<body>
		<div class="main">
			<b>{title}</b>
			<br>
            {account_links}
			<br>
			[<a href="/">Home</a>] [<a href="/status">Status</a>] [<a href="/posts">Public posts</a><span>] [</span><a href="/topics">Topics</a><span>]
            <br>
            {banner}
			<hr>
            <pre>{main_content}</pre>
			<hr>
            <pre>{footer_content}
Copyright &copy; 2025 0x4248 and Contributors
Under the GNU General Public License v3.0
<a href="/privacy">Privacy Policy</a> / <a href="/terms">Terms of Service</a> 
			</pre>
		</div>
	</body>
</html>
"""

def get_account_links(request: Request):
    user = sessions_manager.get_current_user(request)

    if user:
        return f"[<a href='/account/{user}'>{user}</a>] [<a href='/account'>Account settings</a>] [<a href='/logout'>Logout</a>] [<a href='/new_post'>New post</a>]"
    else:
        return "[<a href='/login'>Login</a>] [<a href='/register'>Register</a>] You are not logged in."

def get_username_tag(user):
    if database.User.Get.role(user) == "owner":
        return f"<span class=\"owner_role\">OWNER</span>"
    if database.User.Get.role(user) == "admin":
        return f"<span class=\"admin_role\">ADMIN</span>"
    if database.User.Get.role(user) == "moderator":
        return f"<span class=\"moderator_role\">MOD</span>"
    if database.User.Get.role(user) == "user":
        return f"<span class=\"member_role\">MEMBER</span>"

def get_stats():
    posts = database.PublicPosts.Core.get_all_posts()
    users = database.User.Core.get_all_users()
    topics = database.Topics.Core.get_all_topics()
    posts_count = len(posts)
    users_count = len(users)
    topics_count = len(topics)
    uptime = datetime.now() - datetime.fromtimestamp(globals.START_TIME)

    main_content = f"""
    System UP
    <b>UPTIME:</b> {uptime.days} days, {uptime.seconds // 3600} hours, {(uptime.seconds // 60) % 60} minutes
    <b>VERSION:</b> {globals.VERSION_FULL}
    <b>TOTAL POSTS:</b> {posts_count}
    <b>TOTAL USERS:</b> {users_count}
    <b>TOTAL TOPICS:</b> {topics_count}
    """    

    
    return None