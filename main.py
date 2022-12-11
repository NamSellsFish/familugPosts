import sqlite3
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template

# Get Data
ses = requests.session()
posts = {"Python": [], "Command": [], "sysadmin": []}
for articles in posts:
    ses = requests.get(f"https://www.familug.org/search/label/{articles}")
    soup = BeautifulSoup(ses.content, "html.parser")
    posts[articles] = [
        "{} ({})".format(title.text.strip("\n"), title.find_next().attrs.get("href"))
        for title in soup.find_all("h3", class_="post-title entry-title")
    ]
ses = requests.get("https://familug.github.io/")
soup = BeautifulSoup(ses.content, "html.parser")
posts["latest"] = [
    "{} ({})".format(
        title.find_next().text.strip("\n  "), title.find_next().attrs.get("href")
    )
    for title in soup.find_all("div", class_="recent-posts-article")
][:10]

# Work with database
con = sqlite3.connect("POSTS.db", check_same_thread=False)
cur = con.cursor()
cur.execute(
    "CREATE TABLE IF NOT EXISTS POSTS(No INTERGER,Topic TEXT,details TEXT UNIQUE)"
)
for articles in posts:
    for index, article in enumerate(posts[articles], 1):
        cur.execute(
            f"""
        INSERT OR IGNORE INTO POSTS VALUES
                {(index, articles, article)}
        """
        )
        con.commit()

# Work with website
app = Flask("myapp")


@app.route("/")
def showThePost():
    postsJSON = []
    for articles in posts:
        postsJSON.append(
            list(cur.execute(f"SELECT * FROM POSTS WHERE Topic = '{articles}' "))
        )
    return render_template(
        "index.html",
        posts=postsJSON,
    )


if __name__ == "__main__":
    app.run(debug=True)
