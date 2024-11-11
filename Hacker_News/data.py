'''This module gets the 50 newest stories from the hacker news api and adds it to
the Post databse'''
import datetime
import sys
import requests
from hackernews import app, db
from hackernews.models import Post, Role

def fetch_and_store_stories():
    URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
    response = requests.get(URL, timeout=10)
    if response.status_code != 200:
        sys.exit()
    html = response.json()
    with app.app_context():
        #db.drop_all()
        db.create_all()
        roles_to_create = ['member', 'admin']
        for role_name in roles_to_create:
            existing_role = Role.query.filter_by(name=role_name).first()
            if not existing_role:
                new_role = Role(name=role_name)
                db.session.add(new_role)
        COUNT = 0
        for i in range(50):
            response = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{html[i]}.json",
                    timeout=10)
            if response.status_code == 200:
                post = response.json()
            if post.get('type') != 'story' or post.get('url') is None:
                continue
            p = Post(author=post.get('by'), descendants=post.get('descendants'), id=post['id'],
                    kids=post.get('kids'), score=post.get('score'), posttype=post.get('type'),
                    title=post.get('title'), time=post.get('time'), url=post.get('url'), popularity=0)
            exists = db.session.query(Post).filter_by(id=post['id']).count()
            if not exists:
                db.session.add(p)
                db.session.commit()
                COUNT+=1
    ct = datetime.datetime.now()
    print(f"Datestamp: {ct}, Saved {COUNT} new stories")
    return COUNT

if __name__ == "__main__":
    fetch_and_store_stories()
