
import sqlite3
import os

from lib import xss

conn = sqlite3.connect("data/nexo.db")
conn.row_factory = sqlite3.Row
c = conn.cursor()


def generate_databases():
    c.execute("CREATE TABLE IF NOT EXISTS Users (Username TEXT, Password TEXT, Role TEXT, Banned TEXT, BanReason TEXT, AboutMe TEXT, AccountSettings TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS PublicPosts (ID TEXT, Title TEXT, Author TEXT, Timestamp TEXT, Topic TEXT, Body TEXT, Attachments TEXT, Score INTEGER, Deleted TEXT, Archived TEXT, RepliesLocked TEXT, Replies TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS PublicPostsReplies (ID TEXT, PostID TEXT, Author TEXT, Timestamp TEXT, Body TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS Topics (ID TEXT, Name TEXT, Description TEXT, AdminOnly TEXT, Locked TEXT, Archived TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS DirectMessages (ID TEXT, Sender TEXT, Recipient TEXT, Timestamp TEXT, Body TEXT, ReadByRecipient TEXT, Replies TEXT)")
    conn.commit()

class User:
    class Core:
        def get_user(username):
            c.execute("SELECT * FROM Users WHERE Username = ?", (username,))
            row = c.fetchone()
            return dict(row) if row else None
        
        def create_user(username, password, role):
            username = xss.sanitize_input_no_html(username)
            password = xss.sanitize_input_no_html(password)
            role = xss.sanitize_input_no_html(role)
            c.execute("INSERT INTO Users (Username, Password, Role) VALUES (?, ?, ?)", (username, password, role))
            conn.commit()
    
        def update_user(username, password, role, banned, ban_reason, about_me, account_settings):
            username = xss.sanitize_input_no_html(username)
            password = xss.sanitize_input_no_html(password)
            role = xss.sanitize_input_no_html(role)
            banned = xss.sanitize_input_no_html(banned)
            ban_reason = xss.sanitize_input_no_html(ban_reason)
            about_me = xss.sanitize_input_no_html(about_me)
            account_settings = xss.sanitize_input_no_html(account_settings)
            
            c.execute("UPDATE Users SET Password = ?, Role = ?, Banned = ?, BanReason = ?, AboutMe = ?, AccountSettings = ? WHERE Username = ?", (password, role, banned, ban_reason, about_me, account_settings, username))
            conn.commit()
        
        def get_all_users():
            c.execute("SELECT * FROM Users")
            rows = c.fetchall()
            return [dict(row) for row in rows]
        
        def get_user_by_role(role):
            c.execute("SELECT * FROM Users WHERE Role = ?", (role,))
            rows = c.fetchall()
            return [dict(row) for row in rows]
        
        def get_user_by_ban_status(banned):
            c.execute("SELECT * FROM Users WHERE Banned = ?", (banned,))
            rows = c.fetchall()
            return [dict(row) for row in rows]
    
    class Set:
        def ban_status(username, status, reason):
            status = xss.sanitize_input_no_html(status)
            reason = xss.sanitize_input_no_html(reason)
            c.execute("UPDATE Users SET Banned = ?, BanReason = ? WHERE Username = ?", (status, reason, username))
            conn.commit()
        
        def user_role(username, role):
            c.execute("UPDATE Users SET Role = ? WHERE Username = ?", (role, username))
            conn.commit()
        
        def about_me(username, about_me):
            about_me = xss.sanitize_input_no_html(about_me)
            c.execute("UPDATE Users SET AboutMe = ? WHERE Username = ?", (about_me, username))
            conn.commit()
            
        def account_settings(username, settings):
            settings = xss.sanitize_input_no_html(settings)
            c.execute("UPDATE Users SET AccountSettings = ? WHERE Username = ?", (settings, username))
            conn.commit()
        
        def password(username, password):
            password = xss.sanitize_input_no_html(password)
            c.execute("UPDATE Users SET Password = ? WHERE Username = ?", (password, username))
            conn.commit()
        
        # TODO: User deleting / Need to update entire database to make a ghost user
        
        def delete_user(username):
            pass
        
    class Get:
        def about_me(username):
            c.execute("SELECT AboutMe FROM Users WHERE Username = ?", (username,))
            row = c.fetchone()
            return row[0] if row else None
        
        def account_settings(username):
            c.execute("SELECT AccountSettings FROM Users WHERE Username = ?", (username,))
            row = c.fetchone()
            return row[0] if row else None
        
        def password(username):
            c.execute("SELECT Password FROM Users WHERE Username = ?", (username,))
            row = c.fetchone()
            return row[0] if row else None
        
        def role(username):
            c.execute("SELECT Role FROM Users WHERE Username = ?", (username,))
            row = c.fetchone()
            return row[0] if row else None
        
        def banned(username):
            c.execute("SELECT Banned FROM Users WHERE Username = ?", (username,))
            row = c.fetchone()
            return row[0] if row else None
        
        def ban_reason(username):
            c.execute("SELECT BanReason FROM Users WHERE Username = ?", (username,))
            row = c.fetchone()
            return row[0] if row else None
        
    class Check:
        def exists(username):
            c.execute("SELECT * FROM Users WHERE Username = ?", (username,))
            row = c.fetchone()
            return True if row else False
        
        def is_banned(username):
            c.execute("SELECT Banned FROM Users WHERE Username = ?", (username,))
            row = c.fetchone()
            return True if row and row[0] == "True" else False
        
        def is_admin(username):
            admin_roles = ["admin", "superadmin", "administrator", "mod", "moderator", "owner", "staff", "team"]
            c.execute("SELECT Role FROM Users WHERE Username = ?", (username,))
            row = c.fetchone()
            return True if row and row[0] in admin_roles else False
        
class Topics:
    class Core:
        def get_topic(id):
            c.execute("SELECT * FROM Topics WHERE ID = ?", (id,))
            row = c.fetchone()
            return dict(row) if row else None
        
        def create_topic(id, name, description, admin_only, locked, archived):
            id = xss.sanitize_input_no_html(id)
            name = xss.sanitize_input_no_html(name)
            description = xss.sanitize_input_no_html(description)
            admin_only = xss.sanitize_input_no_html(admin_only)
            locked = xss.sanitize_input_no_html(locked)
            archived = xss.sanitize_input_no_html(archived)
            
            c.execute("INSERT INTO Topics (ID, Name, Description, AdminOnly, Locked, Archived) VALUES (?, ?, ?, ?, ?, ?)", (id, name, description, admin_only, locked, archived))
            conn.commit()
            
        def update_topic(id, name, description, admin_only, locked, archived):
            id = xss.sanitize_input_no_html(id)
            name = xss.sanitize_input_no_html(name)
            description = xss.sanitize_input_no_html(description)
            admin_only = xss.sanitize_input_no_html(admin_only)
            locked = xss.sanitize_input_no_html(locked)
            archived = xss.sanitize_input_no_html(archived)
            
            c.execute("UPDATE Topics SET Name = ?, Description = ?, AdminOnly = ?, Locked = ?, Archived = ? WHERE ID = ?", (name, description, admin_only, locked, archived, id))
            conn.commit()
        
        def get_all_topics():
            c.execute("SELECT * FROM Topics")
            rows = c.fetchall()
            return [dict(row) for row in rows]
        
        def get_topic_by_admin_only(admin_only):
            c.execute("SELECT * FROM Topics WHERE AdminOnly = ?", (admin_only,))
            rows = c.fetchall()
            return [dict(row) for row in rows]
        
        def get_topic_by_locked(locked):
            c.execute("SELECT * FROM Topics WHERE Locked = ?", (locked,))
            rows = c.fetchall()
            return [dict(row) for row in rows]
        
        def get_topic_by_archived(archived):
            c.execute("SELECT * FROM Topics WHERE Archived = ?", (archived,))
            rows = c.fetchall()
            return [dict(row) for row in rows]

class PublicPosts:
    class Core:
        def add_post(id, title, author, timestamp, topic, body="", attachments="[]", score=0, deleted="False", archived="False", replies_locked="False", replies="[]"):
            title = xss.sanitize_input_no_html(title)
            author = xss.sanitize_input_no_html(author)
            topic = xss.sanitize_input_no_html(topic)
            body = xss.sanitize_markdown_input(body)

            c.execute("""
                INSERT INTO PublicPosts (ID, Title, Author, Timestamp, Topic, Body, Attachments, Score, Deleted, Archived, RepliesLocked, Replies)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (id, title, author, timestamp, topic, body, attachments, score, deleted, archived, replies_locked, replies)
            )
            conn.commit()
        
        def delete_post(id):
            c.execute("DELETE FROM PublicPosts WHERE ID = ?", (id,))
            conn.commit()

        def get_post(id):
            c.execute("SELECT * FROM PublicPosts WHERE ID = ?", (id,))
            row = c.fetchone()
            return dict(row) if row else None

        def get_all_posts():
            c.execute("SELECT * FROM PublicPosts ORDER BY Timestamp DESC")
            return [dict(row) for row in c.fetchall()]

        def get_posts_by_user(author):
            c.execute("SELECT * FROM PublicPosts WHERE Author = ? ORDER BY Timestamp DESC", (author,))
            return [dict(row) for row in c.fetchall()]
        
        def get_posts_by_topic(topic):
            c.execute("SELECT * FROM PublicPosts WHERE Topic = ? ORDER BY Timestamp DESC", (topic,))
            return [dict(row) for row in c.fetchall()]

        def get_post_by_page(page):
            c.execute("SELECT * FROM PublicPosts ORDER BY Timestamp DESC LIMIT 20 OFFSET ?", (page * 20,))
            return [dict(row) for row in c.fetchall()]

    class Set:
        def lock_replies(id, lock_status="True"):
            c.execute("UPDATE PublicPosts SET RepliesLocked = ? WHERE ID = ?", (lock_status, id))
            conn.commit()

        def archive(id):
            c.execute("UPDATE PublicPosts SET Archived = 'True' WHERE ID = ?", (id,))
            conn.commit()

        def soft_delete(id):
            c.execute("UPDATE PublicPosts SET Deleted = 'True' WHERE ID = ?", (id,))
            conn.commit()

        def update_score(id, score):
            c.execute("UPDATE PublicPosts SET Score = ? WHERE ID = ?", (score, id))
            conn.commit()

        def update_body(id, body):
            body = xss.sanitize_markdown_input(body)
            c.execute("UPDATE PublicPosts SET Body = ? WHERE ID = ?", (body, id))
            conn.commit()

    class Check:
        def exists(id):
            c.execute("SELECT * FROM PublicPosts WHERE ID = ?", (id,))
            return c.fetchone() is not None

class PublicPostReplies:
    class Core:
        def add_reply(reply_id, post_id, author, timestamp, body):
            author = xss.sanitize_input_no_html(author)
            body = xss.sanitize_markdown_input(body)
            c.execute("""
                INSERT INTO PublicPostsReplies (ID, PostID, Author, Timestamp, Body)
                VALUES (?, ?, ?, ?, ?)""", 
                (reply_id, post_id, author, timestamp, body)
            )
            conn.commit()

        def get_replies(post_id):
            c.execute("SELECT * FROM PublicPostsReplies WHERE PostID = ? ORDER BY Timestamp ASC", (post_id,))
            return [dict(row) for row in c.fetchall()]
        
        def get_reply(reply_id):
            c.execute("SELECT * FROM PublicPostsReplies WHERE ID = ?", (reply_id,))
            row = c.fetchone()
            return dict(row) if row else None

        def delete_reply(reply_id):
            c.execute("DELETE FROM PublicPostsReplies WHERE ID = ?", (reply_id,))
            conn.commit()

    class Check:
        def exists(reply_id):
            c.execute("SELECT * FROM PublicPostsReplies WHERE ID = ?", (reply_id,))
            return c.fetchone() is not None
