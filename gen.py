#!/usr/local/bin/python3

import sqlite3
from datetime import datetime
from jinja2 import Environment,FileSystemLoader,select_autoescape,Template
from math import ceil
import os
import configparser

# Read from the settings config file.
# Basically contains the password and username for email login. There is probably a way better way to do this.
config = configparser.ConfigParser()
config.read("settings.cfg")

#Configure the Jinja2 template environment.
#Used to generate the RSS and html pages.

env = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=select_autoescape(
        enabled_extensions=('html', 'rss'),
        default_for_string=True,
        default=True
    )
)

#A pub date filter function. Used to format post dates in the style that I like.
#TODO make it use the datetime tag in html

def pub_date(date):
    return datetime.strptime(date,"%m/%d/%y").strftime("%a, %d %b %Y 00:00:00 +0000")

env.filters["pub_date"] = pub_date

#This probably should be read from the config file...
POSTS_DB="posts.db"
posts = env.get_template("index.html")
feed = env.get_template("feed.rss")

try:
    conn=sqlite3.connect(POSTS_DB, timeout=1000)
except sqlite3.Error as e:
    print(e)

#This just makes sure we throw all of our files in an output directory.
    
os.chdir(config["posts"]["directory"])
if os.path.isdir("output"):
    pass
try:
    os.mkdir("output")
except FileExistsError:
    pass
    

cur = conn.cursor()

#Get a postcount. Could be kept better track by having a postcount field in the DB.
"""
Sort by descending.

Get number of items in DB

Sub 10 from that number -> X

SELECT * LIMIT 10 from index X

Create page

Repeat until X < 10

If X < 10 then set index to 0.
"""

try:
    # A count of all entries in the database. Does not include duplicates.
    entry_count = cur.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
    # Get a max number of 10 entries per page.
    max_pages = entry_count // 10
    # Loop down starting from the last post and create pages. 
    page = max_pages
    i = entry_count
    # While we still have posts to grab; grab more posts.
    while page >= 0:
        # Grabs all the posts starting from `i` and ending 10 posts later. Sort them properly. etc.
        cur.execute("SELECT date,content FROM posts ORDER BY stamp DESC LIMIT 10 OFFSET (?)",(i-10,))
        entries = cur.fetchall()
        print("page", page)
        print("i", i, "/", entry_count)
        print("\n".join(map(lambda x: x[0]+" "+str(x[1][:32]),entries)))
        # Page naming code...
        # Move this into a function so that we can use some sort of data structure to get URLs.
        name = "page{}.html".format(page)
        next_page_link = None
        if page == 0:
            name = "index.html"
            feed.stream(posts = entries, pub_date = pub_date).dump("output/feed.rss")
        crumbs = [None, None]
        if page == 1:
            crumbs[0] = f"/index.html"
        elif page != 0:
            crumbs[0] = f"/page{page - 1}.html"
        if page == max_pages:
            crumbs[1] = f"/log.txt"
        elif page < max_pages:
            crumbs[1] = f"/page{page + 1}.html"
        # Save the 10 posts to an HTML file.
        posts.stream(posts = entries, crumbs = crumbs).dump("output/"+name)
        i -= 10
        if i < 0: i = 0
        page -= 1
    
except KeyboardInterrupt:
    print("abort! abort!")
finally:
    conn.close()
