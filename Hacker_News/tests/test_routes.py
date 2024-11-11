'''Testing the routes.py module'''
import re
import pytest
from hackernews import app, db
from hackernews.models import User, Post, Role

@pytest.fixture()
def client():
    '''simulates a user that is not logged in'''
    return app.test_client()

@pytest.fixture
def authenticated_client():
    '''simulates a user that is logged in'''
    test_client = app.test_client()
    with test_client.session_transaction() as sess:
        sess['user'] = {
                'userinfo':{
                    'name': 'Test User',
                    'email': 'test.user@gmail.com',
                    'sub': 'testid',
                    'picture': 'https://images.app.goo.gl/mzUFQFSnSQPp7sZ76'
                }
        }
    return test_client

def test_about_page(client):
    '''tests if the about page returns correctly'''
    response = client.get("/about")
    assert response.status_code == 200
    assert b"<h1>About Page</h1>" in response.data

def test_logout_redirect(client):
    '''tests if logging out redirects'''
    response = client.get("/logout")
    assert response.status_code == 302
    data_string = response.data.decode('utf-8')
    start_index = data_string.find('<a href="') + len('<a href="')
    end_index = data_string.find('">', start_index)
    redirection_url = data_string[start_index:end_index]
    assert redirection_url == "https://dev-bppiraw33sqksk0i.us.auth0.com/v2/logout?returnTo=http%3A%2F%2Flocalhost%2Fhome&amp;client_id=yVGXMLnSqOUQmm3DXOqB2PZKggEYTTsR"

def test_get_admin_redirect(authenticated_client):
    '''tests if get_admin redirects home'''
    new_user = User(id='testid', username="Test User", email="test.user@gmail.com",
            image_file="https://images.app.goo.gl/mzUFQFSnSQPp7sZ76")
    with app.app_context():
        db.session.add(new_user)
        db.session.commit()

    response = authenticated_client.get("/get_admin")

    with app.app_context():
        retrieved_user = User.query.filter_by(id='testid').first()
        db.session.delete(retrieved_user)
        db.session.commit()

    assert response.status_code == 302
    assert response.location == "/home"

def test_login_redirect(client):
    '''tests if login redirects a user to auth0'''
    response = client.get("/login")
    data_string = response.data.decode('utf-8')
    start_index = data_string.find('<a href="') + len('<a href="')
    end_index = data_string.find('">', start_index)
    redirection_url = data_string[start_index:end_index]
    expected_base_url = "https://dev-bppiraw33sqksk0i.us.auth0.com/authorize?response_type=code&amp;client_id=yVGXMLnSqOUQmm3DXOqB2PZKggEYTTsR&amp;redirect_uri=http%3A%2F%2Flocalhost%2Fcallback&amp;scope=openid+profile+email"
    assert response.status_code == 302
    assert redirection_url.startswith(expected_base_url)
    assert re.search(r'state=.+&amp;nonce=.+', redirection_url) is not None

def test_home_page(client):
    '''tests if the home page displays'''
    response = client.get("/home")
    assert response.status_code == 200

def test_account_page(authenticated_client):
    '''tests if the profile displays for logged in users'''
    response = authenticated_client.get("/account")
    assert response.status_code == 200
    assert b"<h1>Profile</h1>" in response.data
    assert b"Test User" in response.data
    assert b"https://images.app.goo.gl/mzUFQFSnSQPp7sZ76" in response.data
    assert b"test.user@gmail.com" in response.data

def test_account_page_unauthorized(client):
    '''tests if accessing the profile page redirects for not logged in users'''
    response = client.get("/account")
    assert response.status_code == 302
    assert response.location == "/login"

def test_newsfeed(client):
    '''tests if newsfeed route works'''
    response = client.get("/newsfeed")
    assert response.status_code == 200

def test_like_post(authenticated_client):
    '''simulates all ways to like a post'''
    # Create a user object using the SQLAlchemy model
    new_user = User(id='testid', username="Test User", email="test.user@gmail.com",
            image_file="https://images.app.goo.gl/mzUFQFSnSQPp7sZ76")
    new_post = Post(id=1, author="test author", title="test title",
            url="https://www.lipsum.com/")
    # Add the new user to the session and commit to the database
    with app.app_context():
        db.session.add(new_user)
        db.session.add(new_post)
        db.session.commit()

    # Query the database to retrieve the newly created user
        retrieved_user = User.query.filter_by(id='testid').first()
        retrieved_post = Post.query.filter_by(id=1).first()
    # Assert that the retrieved user matches the expected username
    assert retrieved_user.username == 'Test User'
    assert retrieved_post.title == "test title"

    response = authenticated_client.post('/like-post/1')
    assert response.status_code == 200
    assert b'{"dislikes":0,"liked":true,"likes":1}' in response.data

    response = authenticated_client.post('/like-post/1')
    assert response.status_code == 200
    assert b'{"dislikes":0,"liked":false,"likes":0}' in response.data

    authenticated_client.post('/dislike-post/1')
    response = authenticated_client.post('/like-post/1')
    assert response.status_code == 200
    assert b'{"dislikes":0,"liked":true,"likes":1}' in response.data

    with app.app_context():
        db.session.delete(retrieved_user)
        db.session.delete(retrieved_post)
        db.session.commit()

        deleted_user = User.query.filter_by(id='testid').first()
        deleted_post = User.query.filter_by(id=1).first()
    assert deleted_user is None  # Ensure the user has been deleted from the database
    assert deleted_post is None

def test_dislike_post(authenticated_client):
    '''simulates all 3 ways paths of clicking dislike'''
    # Create a user object using the SQLAlchemy model
    new_user = User(id='testid', username="Test User", email="test.user@gmail.com",
            image_file="https://images.app.goo.gl/mzUFQFSnSQPp7sZ76")
    new_post = Post(id=1, author="test author", title="test title",
            url="https://www.lipsum.com/")
    # Add the new user to the session and commit to the database
    with app.app_context():
        db.session.add(new_user)
        db.session.add(new_post)
        db.session.commit()

    # Query the database to retrieve the newly created user
        retrieved_user = User.query.filter_by(id='testid').first()
        retrieved_post = Post.query.filter_by(id=1).first()
    # Assert that the retrieved user matches the expected username
    assert retrieved_user.username == 'Test User'
    assert retrieved_post.title == "test title"

    response = authenticated_client.post('/dislike-post/1')
    assert response.status_code == 200
    assert b'{"disliked":true,"dislikes":1,"likes":0}' in response.data

    response = authenticated_client.post('/dislike-post/1')
    assert response.status_code == 200
    assert b'{"disliked":false,"dislikes":0,"likes":0}' in response.data

    authenticated_client.post('/like-post/1')
    response = authenticated_client.post('/dislike-post/1')
    assert response.status_code == 200
    assert b'{"disliked":true,"dislikes":1,"likes":0}' in response.data

    with app.app_context():
        db.session.delete(retrieved_user)
        db.session.delete(retrieved_post)
        db.session.commit()

        deleted_user = User.query.filter_by(id='testid').first()
        deleted_post = User.query.filter_by(id=1).first()
    assert deleted_user is None  # Ensure the user has been deleted from the database
    assert deleted_post is None

def test_admin_no_session(client):
    '''tests if you access admin only actions without being logged in'''
    response = client.get("/admin_post")
    assert response.status_code == 302
    assert response.location == '/login'

def test_admin_post(authenticated_client):
    '''tests admin dashboard for posts'''
    new_user = User(id='testid', username="Test User", email="test.user@gmail.com",
            image_file="https://images.app.goo.gl/mzUFQFSnSQPp7sZ76")
    with app.app_context():
        db.session.add(new_user)
        db.session.commit()

        retrieved_user = User.query.filter_by(id='testid').first()
        role = db.session.query(Role).filter_by(name='admin').first()
        retrieved_user.roles.append(role)
        db.session.commit()
    response = authenticated_client.get("/admin_post")
    assert response.status_code == 200
    assert b'<h1>Admin Dashboard </h1>' in response.data
    with app.app_context():
        retrieved_user = User.query.filter_by(id='testid').first()
        db.session.delete(retrieved_user)
        db.session.commit()

def test_admin_user(authenticated_client):
    '''tests admin dashboard for users'''
    new_user = User(id='testid', username="Test User", email="test.user@gmail.com",
            image_file="https://images.app.goo.gl/mzUFQFSnSQPp7sZ76")
    with app.app_context():
        db.session.add(new_user)
        db.session.commit()

        retrieved_user = User.query.filter_by(id='testid').first()
        role = db.session.query(Role).filter_by(name='admin').first()
        retrieved_user.roles.append(role)
        db.session.commit()
    response = authenticated_client.get("/admin_user")
    assert response.status_code == 200
    assert b'<h1>Admin Dashboard </h1>' in response.data
    with app.app_context():
        retrieved_user = User.query.filter_by(id='testid').first()
        db.session.delete(retrieved_user)
        db.session.commit()

def test_delete_user(authenticated_client):
    '''tests admin task of deleting users'''
    new_user = User(id='testid', username="Test User", email="test.user@gmail.com",
            image_file="https://images.app.goo.gl/mzUFQFSnSQPp7sZ76")
    delete_user = User(id='deleteid', username="Delete User", email="delete.user@gmail.com",
            image_file="https://images.app.goo.gl/mzUFQFSnSQPp7sZ76")
    with app.app_context():
        db.session.add(new_user)
        db.session.add(delete_user)
        db.session.commit()

        retrieved_user = User.query.filter_by(id='testid').first()
        role = db.session.query(Role).filter_by(name='admin').first()
        retrieved_user.roles.append(role)
        db.session.commit()

        retrieved_user_delete = User.query.filter_by(id='deleteid').first()
    assert retrieved_user_delete.username == 'Delete User'

    response = authenticated_client.get("/delete-user/deleteid")

    with app.app_context():
        db.session.delete(retrieved_user)
        db.session.commit()

        admin_user = User.query.filter_by(id='testid').first()
        deleted_user = User.query.filter_by(id='deleteid').first()
    assert response.status_code == 302
    assert admin_user is None
    assert deleted_user is None

def test_delete_post(authenticated_client):
    '''tests admin task of deleting posts'''
    new_user = User(id='testid', username="Test User", email="test.user@gmail.com",
            image_file="https://images.app.goo.gl/mzUFQFSnSQPp7sZ76")
    new_post = Post(id=1, author="test author", title="test title",
            url="https://www.lipsum.com/")
    with app.app_context():
        db.session.add(new_user)
        db.session.add(new_post)
        db.session.commit()

        retrieved_user = User.query.filter_by(id='testid').first()
        role = db.session.query(Role).filter_by(name='admin').first()
        retrieved_user.roles.append(role)
        db.session.commit()

        retrieved_post = Post.query.filter_by(id=1).first()
    assert retrieved_post.title == "test title"

    response = authenticated_client.get("/delete-post/1")

    with app.app_context():
        db.session.delete(retrieved_user)
        db.session.commit()

        admin_user = User.query.filter_by(id='testid').first()
        deleted_post = Post.query.filter_by(id=1).first()
    assert response.status_code == 302
    assert admin_user is None
    assert deleted_post is None
