
import sqlite3
import os

from lib import xss

conn = sqlite3.connect("data/nexo.db")
c = conn.cursor()


def generate_databases():
    c.execute("CREATE TABLE IF NOT EXISTS Users (Username TEXT, Password TEXT, Role TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS PublicPosts (ID TEXT, Title TEXT, Author TEXT, Timestamp TEXT, Topic TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS Mail (ID TEXT, Sender TEXT, Recipient TEXT, Timestamp TEXT, Title TEXT)")
    conn.commit()

class User:
    def add_user(username, password, role):
        username = xss.sanitize_input_no_html(username)
        role = xss.sanitize_input_no_html(role)
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
        
    def get_all_users():
        c.execute("SELECT * FROM Users")
        return c.fetchall()
    
    def get_admins():
        c.execute("SELECT * FROM Users WHERE Role = 'admin'")
        return c.fetchall()

    def is_user_admin(username):
        c.execute("SELECT Role FROM Users WHERE Username = ?", (username,))
        role = c.fetchone()
        if role is None:
            return False
        return role[0] == "admin" or role[0] == "superadmin" or role[0] == "root" or role[0] == "owner" or role[0] == "administrator" or role[0] == "modrrator" or role[0] == "mod"
    
    def get_role(username):
        c.execute("SELECT Role FROM Users WHERE Username = ?", (username,))
        role = c.fetchone()
        if role is None:
            return None
        return role[0]
    
class PublicPosts:
    def add_post(id, title, author, timestamp, topic):
        title = xss.sanitize_input_no_html(title)
        author = xss.sanitize_input_no_html(author)
        topic = xss.sanitize_input_no_html(topic)
        title = title[:100]
        c.execute("INSERT INTO PublicPosts (ID, Title, Author, Timestamp, Topic) VALUES (?, ?, ?, ?, ?)", (id, title, author, timestamp, topic))
        conn.commit()
    
    def get_post(id):
        c.execute("SELECT * FROM PublicPosts WHERE ID = ?", (id,))
        return c.fetchone()

    def get_all_posts():
        c.execute("SELECT * FROM PublicPosts")
        return c.fetchall()
    
    def get_post_by_page(page):
        c.execute("SELECT * FROM PublicPosts ORDER BY Timestamp DESC LIMIT 20 OFFSET ?", (page * 20,))
        return c.fetchall()

    def delete_post(id):
        c.execute("DELETE FROM PublicPosts WHERE ID = ?", (id,))
        conn.commit()
        
    def get_posts_by_user(username):
        c.execute("SELECT * FROM PublicPosts WHERE Author = ?", (username,))
        return c.fetchall()
    
    def get_posts_by_topic(topic):
        c.execute("SELECT * FROM PublicPosts WHERE Topic = ?", (topic,))
        return c.fetchall()
    
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
