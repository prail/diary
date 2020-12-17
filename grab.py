#!/usr/local/bin/python3
from imaplib import IMAP4_SSL
import email
from datetime import datetime
import sqlite3
import configparser

config = configparser.ConfigParser()
config.read("settings.cfg")

HOST=config["email"]["host"]
PORT=config["email"]["port"]
USER=config["email"]["username"]
PASSWD=config["email"]["password"]
FILTER_SUBJECT=config["posts"]["filter_subject"]
DB=config["posts"]["database"]

SQLITE_DB_SCHEMA='''CREATE TABLE IF NOT EXISTS posts (
    date TEXT PRIMARY KEY,
    stamp INTEGER,
    content TEXT
);\
'''

SQLITE_UPDATEPOST='''\
INSERT INTO posts(date,stamp,content) VALUES(?,?,?)
    ON CONFLICT(date)
        DO UPDATE SET
            content=excluded.content,
            stamp=excluded.stamp
        WHERE excluded.stamp>posts.stamp;\
'''

posts=[]
with IMAP4_SSL(HOST, PORT) as M:
    M.login(USER, PASSWD)
    M.enable("UTF8=ACCEPT")
    M.select()
    typ, data = M.search(None, 'FROM "{}" SUBJECT "{}"'.format(USER,FILTER_SUBJECT))
    for num in data[0].split():
        typ, data = M.fetch(num, '(RFC822)')
        s = data[0][1].decode()
        msg = email.message_from_string(s)
        if msg["subject"].lower() == FILTER_SUBJECT.lower():
            post_date = datetime.strptime(msg["date"],"%a, %d %b %Y %H:%M:%S %z")
            if msg["Content-Type"].split(";")[0] == "text/plain":
                post_content = msg.get_payload(decode=True).decode("utf-8").strip()
                posts.append((post_date.strftime("%m/%d/%y"),post_date.timestamp(),post_content))
    M.close()
    M.logout()
try:
    conn = sqlite3.connect(DB, timeout=1000)
except sqlite3.Error as e:
    print(e)
    exit(1)
    
cursor = conn.cursor()
cursor.execute(SQLITE_DB_SCHEMA)
conn.commit()
if len(posts) > 0:
    print(f"Attempting to add/update {len(posts)} posts...")
    for p in posts: #p[0]= timestamp p[1] post content fromtimestamp to convert
        try:
            cursor.execute(SQLITE_UPDATEPOST,p)
            conn.commit()
        except sqlite3.Error as e:
            print(e)
    print("Posts updated, Goodbye!")
else:
    print("No posts to add/update, Goodbye!")
conn.close()

