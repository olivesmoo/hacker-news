'''Tests the data.py module'''
import data
from hackernews import app
from hackernews.models import Post

def test_fetch_and_store_stories():
    '''Tests the fetcha_and _store_stories function'''
    with app.app_context():
        total_posts = Post.query.count()
    new_stories = data.fetch_and_store_stories()

    with app.app_context():
        new_total_posts = Post.query.count()
    assert new_total_posts == total_posts+new_stories
