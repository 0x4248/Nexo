import os
import json
from lib import xss

class PublicPosts:
    def add_post(id, title, author, timestamp, topic, content):
        title = xss.sanitize_input_no_html(title)
        author = xss.sanitize_input_no_html(author)
        topic = xss.sanitize_input_no_html(topic)
        content = xss.sanitize_markdown_input(content)
        
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
                "score": 0,
                "attachments": [],
                "deleted": False,
                "arhived": False,
                "replies_locked": False,
                "replies": []}, f, indent=4)
    def get_post(id):
        if not os.path.exists("data/posts/"):
            os.makedirs("data/posts/")
        with open(f"data/posts/{id}.json", "r") as f:
            data = json.load(f)
            return data
        
    def add_reply(id, username , content, timestamp):
        username = xss.sanitize_input_no_html(username)
        content = xss.sanitize_markdown_input(content)
        timestamp = xss.sanitize_input_no_html(timestamp)
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
    
    def delete_post(id):
        if not os.path.exists("data/posts/"):
            os.makedirs("data/posts/")
        with open(f"data/posts/{id}.json", "r") as f:
            data = json.load(f)
            data["deleted"] = True
            with open(f"data/posts/{id}.json", "w") as f:
                json.dump(data, f, indent=4)
                
    def archive_post(id):
        if not os.path.exists("data/posts/"):
            os.makedirs("data/posts/")
        with open(f"data/posts/{id}.json", "r") as f:
            data = json.load(f)
            data["archived"] = True
            with open(f"data/posts/{id}.json", "w") as f:
                json.dump(data, f, indent=4)

class User:
    def set_aboutme(username, aboutme):
        username = xss.sanitize_input_no_html(username)
        aboutme = xss.sanitize_markdown_input(aboutme)
        try:
            os.makedirs(f"data/users/{username}/", exist_ok=True)
            with open(f"data/users/{username}/about.txt", "w") as f:
                f.write(aboutme)
        except Exception as e:
            print(f"[ERROR] Couldn't save about me for {username}: {e}")

    def get_aboutme(username):
        username = xss.sanitize_input_no_html(username)
        try:
            with open(f"data/users/{username}/about.txt", "r") as f:
                data = f.read()
                return data
        except FileNotFoundError:
            return "No about me found"
    def get_profilepic(username):
        username = xss.sanitize_input_no_html(username)
        if not os.path.exists(f"data/users/{username}/profile_pic.png"):
            with open(f"src/static/base.png", "rb") as f:
                data = f.read()
                return data
        with open(f"data/users/{username}/profile_pic.png", "rb") as f:
            data = f.read()
            return data
        
    def set_theme(username, theme):
        username = xss.sanitize_input_no_html(username)
        theme = xss.sanitize_input_no_html(theme)
        try:
            os.makedirs(f"data/users/{username}/", exist_ok=True)
            with open(f"data/users/{username}/theme.txt", "w") as f:
                f.write(theme)
        except Exception as e:
            print(f"[ERROR] Couldn't save theme for {username}: {e}")
    
    def set_color_theme(username, color):
        username = xss.sanitize_input_no_html(username)
        color = xss.sanitize_input_no_html(color)
        try:
            os.makedirs(f"data/users/{username}/", exist_ok=True)
            with open(f"data/users/{username}/color.txt", "w") as f:
                f.write(color)
        except Exception as e:
            print(f"[ERROR] Couldn't save color theme for {username}: {e}")    

class Mail:
    def add_mail(id, sender, recipient, timestamp, title, content):
        # save to json
        if not os.path.exists("data/mail/"):
            os.makedirs("data/mail/")
        with open(f"data/mail/{id}.json", "w") as f:
            json.dump({
                "id": id,
                "sender": sender,
                "recipient": recipient,
                "timestamp": timestamp,
                "title": title,
                "content": content}, f, indent=4)
    def get_mail(id):
        # load from json
        if not os.path.exists("data/mail/"):
            os.makedirs("data/mail/")
        with open(f"data/mail/{id}.json", "r") as f:
            data = json.load(f)
            return data