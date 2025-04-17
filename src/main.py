# SPDX-License-Identifier: GPL-3.0 
# Nexo
# Basic HTTP mailing system
#
# main.py
#
# COPYRIGHT NOTICE
# Copyright (C) 2025 0x4248 and contributors
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the license is not changed.
#
# This software is free and open source. Licensed under the GNU general
# public license version 3.0 as published by the Free Software Foundation.

from fastapi import FastAPI, Request, Header, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse, PlainTextResponse, HTMLResponse, FileResponse
from typing import Annotated
from lib import database
from asyncio import run
from PIL import Image
import uvicorn
import hashlib
import time
import datetime
import base64
import PIL
import os
import sqlite3
import json
import importlib
import sys

conn = sqlite3.connect("data/nexo.db")
c = conn.cursor()

def generate_databases():
	c.execute("CREATE TABLE IF NOT EXISTS Users (Username TEXT, Password TEXT, Role TEXT)")
	c.execute("CREATE TABLE IF NOT EXISTS PublicPosts (ID TEXT, Title TEXT, Author TEXT, Timestamp TEXT, Topic TEXT)")
	c.execute("CREATE TABLE IF NOT EXISTS Mail (ID TEXT, Sender TEXT, Recipient TEXT, Timestamp TEXT, Title TEXT)")
	conn.commit()

class User:
	def add_user(username, password, role):
		c.execute("INSERT INTO Users (Username, Password, Role) VALUES (?, ?, ?)", (username, password, role))
		conn.commit()
	
	def get_user(username):
		c.execute("SELECT * FROM Users WHERE Username = ?", (username,))
		return c.fetchone()

	def user_exists(username):
		c.execute("SELECT * FROM Users WHERE Username = ?", (username,))
		return c.fetchone() is not None
	
	def get_user_role(username):
		c.execute("SELECT Role FROM Users WHERE Username = ?", (username,))
		return c.fetchone()[0]
	
	def set_password(username, password):
		c.execute("UPDATE Users SET Password = ? WHERE Username = ?", (password, username))
		conn.commit()

	def set_role(username, role):
		c.execute("UPDATE Users SET Role = ? WHERE Username = ?", (role, username))
		conn.commit()
	
	def delete_user(username):
		c.execute("DELETE FROM Users WHERE Username = ?", (username,))
		conn.commit()

class PublicPosts:
	def add_post(id, title, author, timestamp, topic):
		c.execute("INSERT INTO PublicPosts (ID, Title, Author, Timestamp, Topic) VALUES (?, ?, ?, ?, ?)", (id, title, author, timestamp, topic))
		conn.commit()
	
	def get_post(id):
		c.execute("SELECT * FROM PublicPosts WHERE ID = ?", (id,))
		return c.fetchone()

	def get_all_posts(self):
		c.execute("SELECT * FROM PublicPosts")
		return c.fetchall()
	
	def get_post_by_page(page):
		c.execute("SELECT * FROM PublicPosts ORDER BY Timestamp DESC LIMIT 20 OFFSET ?", (page * 20,))
		return c.fetchall()

	def delete_post(id):
		c.execute("DELETE FROM PublicPosts WHERE ID = ?", (id,))
		conn.commit()
	
class Mail:
	def add_mail(id, sender, recipient, timestamp, title):
		c.execute("INSERT INTO Mail (ID, Sender, Recipient, Timestamp, Title) VALUES (?, ?, ?, ?, ?)", (id, sender, recipient, timestamp, title))
		conn.commit()
	
	def get_mail(id):
		c.execute("SELECT * FROM Mail WHERE ID = ?", (id,))
		return c.fetchone()

	def get_all_mail(recipient):
		c.execute("SELECT * FROM Mail WHERE Recipient = ?", (recipient,))
		return c.fetchall()

	def get_mail_by_page(recipient, page):
		c.execute("SELECT * FROM Mail WHERE Recipient = ? ORDER BY Timestamp DESC LIMIT 20 OFFSET ?", (recipient, page * 20))
		return c.fetchall()
	
	def delete_mail(id):
		c.execute("DELETE FROM Mail WHERE ID = ?", (id,))
		conn.commit()


class meta_storage:
    class PublicPosts:
        def add_post(id, title, author, timestamp, topic, content):
            # save to json
            if not os.path.exists("data/posts/"):
                os.makedirs("data/posts/")
            with open(f"data/posts/{id}.json", "w") as f:
                json.dump({
                    "id": id,
                    "title": title,
                    "author": author,
                    "timestamp": timestamp,
                    "topic": topic,
                    "content": content,
                    "replies": []}, f, indent=4)
        def get_post(id):
            # load from json
            if not os.path.exists("data/posts/"):
                os.makedirs("data/posts/")
            with open(f"data/posts/{id}.json", "r") as f:
                data = json.load(f)
                return data
            
        def add_reply(id, username , content, timestamp):
            # load from json
            if not os.path.exists("data/posts/"):
                os.makedirs("data/posts/")
            with open(f"data/posts/{id}.json", "r") as f:
                data = json.load(f)
                data["replies"].append({
                    "username": username,
                    "timestamp": timestamp,
                    "content": content
                })
                with open(f"data/posts/{id}.json", "w") as f:
                    json.dump(data, f, indent=4)
            
def generate_html(title="Nexo Messaging System", main_content="Server did not return any content", footer_content="", account_links=""):
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
			</span><a href="/status">Status</a><span> / </span><a href="/posts">Public posts</a><span> / </span><a href="/news">Admin announcements and News</a>
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

app = FastAPI()

@app.get("/")
async def root():
    main_content = "<h1 style='font-size: 2rem;'>NEXO SYSTEM</h1>"
    main_content += "A simple HTTP mailing system<br>"
    main_content += "System <span style='color: #00ff00;'>status</span>: <span style='color: #00ff00;'>OK</span><br>"
    return HTMLResponse(generate_html(main_content=main_content))

@app.get("/status")
async def status():
    main_content = "<style>@keyframes rainbow { 0% { color: #ff0000; } 25% { color: #00ff00; } 50% { color: #0000ff; } 75% { color: #ffff00; } 100% { color: #ff00ff; } }</style>"
    main_content += "<img src=\"https://avatars.githubusercontent.com/u/60709927?v=4\" alt=\"IMAGE\" style=\"width: 100px; height: 100px;\"><br>"
    main_content += "<b style=\"animation: rainbow 5s infinite;\">Server status</b><br>"
    main_content += "<b>Server time:</b> " + str(datetime.datetime.now()) + "<br>"
    main_content += "<b>Server uptime:</b> " + str(datetime.timedelta(seconds=int(time.time() - os.path.getmtime("src/main.py")))) + "<br>"
    main_content += "<b>Server version:</b> 0.1<br>"
    main_content += "<b>Server name:</b> NEXO SYSTEM<br>"
    main_content += str(sys.modules.keys())
    return HTMLResponse(generate_html(main_content=main_content))

@app.get("/posts")
async def posts(page: int = 0):
    posts = PublicPosts.get_post_by_page(page)
    main_content = "<a href=\"/\">Home</a> > <a href=\"/posts\">Public posts</a><br>"
    for post in posts:
        main_content += f"{post[3]} <b>{post[4]}</b> <a href=\"/post/{post[0]}\">{post[1]}</a> <i>{post[2]}</i>\n"
    if not posts:
        main_content = "No posts found"
    footer_content = "200 OK"
    return HTMLResponse(generate_html(title="Public posts", main_content=main_content, footer_content=footer_content))


@app.post("/create_post")
async def create_post(title: Annotated[str, Header()], author: Annotated[str, Header()], topic: Annotated[str, Header()], content: Annotated[str, Header()]):
    id = hashlib.sha256((title + author + topic + content).encode()).hexdigest()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    PublicPosts.add_post(id, title, author, timestamp, topic)
    meta_storage.PublicPosts.add_post(id, title, author, timestamp, topic, content)
    return JSONResponse(content={"status": "success", "id": id})

@app.get("/post/{id}")
async def get_post(id: str):

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
    
    return HTMLResponse(generate_html(main_content=main_content, footer_content="Post read OK, SERVER OK", account_links="<a href=\"/account\">My account</a> / <a href=\"/logout\">Logout</a>"))

@app.post("/reply/{id}")
async def reply_post(id: str, username: Annotated[str, Header()], content: Annotated[str, Header()]):
    
    if not meta_storage.PublicPosts.get_post(id):
        raise HTTPException(status_code=404, detail="Post not found")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    meta_storage.PublicPosts.add_reply(id, username, content, timestamp)
    return JSONResponse(content={"status": "success", "id": id})

@app.get("/style")
async def style():
    return FileResponse("src/static/css/main.css")


@app.middleware("http")
async def log_request_info(request: Request, call_next):
    pre_reqtime = time.time()
    response = await call_next(request)
    post_reqtime = time.time()
    response.headers["server"] = "NEXO"
    response.headers["NEXO-version"] = "0.1"
    response.headers["compute-time"] = str(post_reqtime - pre_reqtime)
    return response

if __name__ == "__main__":
    generate_databases()
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")