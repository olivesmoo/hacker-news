'''Routes for hackernews website'''
from urllib.parse import quote_plus, urlencode

import traceback
import datetime
import secrets
from functools import wraps
from flask import redirect, render_template, session, url_for, jsonify, request, abort
from hackernews import app, db, oauth, env
from hackernews.models import User, Post, Like, Dislike, Role

#URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
nonce_val =secrets.token_urlsafe(32)
def is_authenticated(func):
    '''Checks if user is logged in'''
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not session:
            session['next'] = request.url
            return redirect(url_for('login'))  # Redirect to login page if access token is not found
        # Further validation can be performed using Auth0's token validation methods
        return func(*args, **kwargs)
    return decorated_function

def admin_required(func):
    '''Checks if user has admin role'''
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not session:
            return redirect(url_for('login'))
        userid = session.get('user').get('userinfo').get('sub')
        with app.app_context():
            user_roles = db.session.query(User).filter_by(id=userid).first().roles
        role_names = [role.name for role in user_roles]
        #print(role_names, file=open('/home/olives/Hacker_News/hackernews/output.txt', 'a'))
        if 'admin' not in role_names:
            return abort(403)
        return func(*args, **kwargs)
    return decorated_function

@app.after_request
def add_security_headers(response):
    '''Adding CSP Headers to increase security'''
    response.headers['Content-Security-Policy'] = (
            "default-src 'none';"
            "form-action 'none';"
            "connect-src 'self';"
            "base-uri 'self';"
            "style-src 'self'  https://cdnjs.cloudflare.com https://cdn.jsdelivr.net;"
            "script-src 'self' https://cdn.jsdelivr.net "
            f"https://cdnjs.cloudflare.com 'nonce-{nonce_val}';"
            "font-src 'self' https://cdnjs.cloudflare.com;"
            "img-src 'self' https://lh3.googleusercontent.com;"
            "frame-ancestors 'self'"
            )
    return response

@app.route("/login")
def login():
    '''Calls Auth0 to handle login, which redirects to callback'''
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

@app.route("/")
@app.route("/home")
def home():
    '''Renders the home page'''
    posts = []
    with app.app_context():
        page = request.args.get('page', 1, type=int)
        all_posts = db.session.query(Post).order_by(Post.popularity.desc(),
                Post.time.desc()).paginate(page=page, per_page=5)
    for i in all_posts.items:
        num_likes = Like.query.filter_by(post_id=i.id).count()
        num_dislikes = Dislike.query.filter_by(post_id=i.id).count()
        user_likes = Like.query.filter_by(post_id=i.id).all()
        user_dislikes = Dislike.query.filter_by(post_id=i.id).all()
        entry = {
                    'by': i.author,
                    'descendants': i.descendants,
                    'id': i.id,
                    'kids': i.kids,
                    'score': i.score,
                    'title': i.title,
                    'type': i.posttype,
                    'time': datetime.datetime.fromtimestamp(i.time),
                    'url': i.url,
                    'likes': num_likes,
                    'dislikes': num_dislikes,
                    'likedby': user_likes,
                    'dislikedby': user_dislikes
                }
        posts.append(entry)
    return render_template('home.html', posts=posts, page=page,
            pages=list(all_posts.iter_pages(left_edge=1, right_edge=1, left_current=1,
                right_current=2)), nonce_val=nonce_val)

@app.route("/callback", methods=["GET", "POST"])
def callback():
    '''Redirect from Auth0. Collects session information after login'''
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    profile = token.get('userinfo')
    if profile:
        user_id = profile.get('sub')
        existing_user = db.session.query(User).filter_by(id=user_id).first()
        #print(existing_user, file=open('/home/olives/Hacker_News/hackernews/output.txt', 'a'))
        if not existing_user:
            curr_user = User(id=user_id, username=profile.get('name'),
                    email=profile.get('email'), image_file=profile.get('picture'))
            with app.app_context():
                db.session.add(curr_user)
                db.session.flush()

                member_role = Role.query.filter_by(name='member').first()
                if member_role:
                    curr_user.roles.append(member_role)
                db.session.commit()
        user_roles = db.session.query(User).filter_by(id=user_id).first().roles
        role_names = [role.name for role in user_roles]
        session['roles'] = role_names

    if "next" in session:
        next_url = session['next']
        session.pop('next', None)
        return redirect(next_url)

    return redirect("/")

@app.route("/logout")
def logout():
    '''Logout functionality handled by Auth0'''
    session.clear()
    return redirect(
        "https://" + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

@app.route("/about")
def about():
    '''Gets and renders about page for website'''
    return render_template('about.html', title='About')

@app.route("/account")
@is_authenticated
def account():
    '''Renders the user profile page, only if logged in'''
    return render_template('account.html', title='Account')

@app.route('/newsfeed', methods=['GET'])
def get_posts():
    '''Returns json for the 30 most recent posts from the hacker news api'''
    posts = []
    with app.app_context():
        all_posts = db.session.query(Post).order_by(Post.time.desc()).limit(30).all()
    for i in all_posts:
        entry = {
                    'by': i.author,
                    'descendants': i.descendants,
                    'id': i.id,
                    'kids': i.kids,
                    'score': i.score,
                    'title': i.title,
                    'type': i.posttype,
                    'time': i.time,
                    'url': i.url
                }
        posts.append(entry)
    return jsonify({"news_items": posts})

@app.route("/like-post/<post_id>", methods=['POST'])
@is_authenticated
def like(post_id):
    '''Post request to like a post'''
    with app.app_context():
        userid = session.get('user').get('userinfo').get('sub')
        post = db.session.query(Post).filter_by(id=post_id).first()
        curr_like = db.session.query(Like).filter_by(author=userid, post_id=post_id).first()
    if post:
        if curr_like:
            with app.app_context():
                db.session.delete(curr_like)
                if post.popularity > 0:
                    post.popularity -= 1
                    db.session.add(post)
                db.session.commit()
            liked = False
        else:
            curr_like = Like(author=userid, post_id=post_id)
            with app.app_context():
                curr_dislike = db.session.query(Dislike).filter_by(author=userid,
                        post_id=post_id).first()
                if curr_dislike:
                    db.session.delete(curr_dislike)
                else:
                    post.popularity += 1
                    db.session.add(post)
                db.session.add(curr_like)
                db.session.commit()
            liked = True
    with app.app_context():
        numlikes = Like.query.filter_by(post_id=post_id).count()
        numdislikes = Dislike.query.filter_by(post_id=post_id).count()
    #return redirect(url_for('home'))
    return jsonify({"likes": numlikes, "liked": liked, "dislikes": numdislikes})

@app.route("/dislike-post/<post_id>", methods=['POST'])
@is_authenticated
def dislike(post_id):
    '''Post request to dislike a post'''
    with app.app_context():
        userid = session.get('user').get('userinfo').get('sub')
        post = db.session.query(Post).filter_by(id=post_id).first()
        curr_dislike = db.session.query(Dislike).filter_by(author=userid, post_id=post_id).first()
    if post:
        if curr_dislike:
            with app.app_context():
                db.session.delete(curr_dislike)
                if post.popularity > 0:
                    post.popularity -= 1
                    db.session.add(post)
                db.session.commit()
            disliked = False
        else:
            curr_dislike = Dislike(author=userid, post_id=post_id)
            with app.app_context():
                curr_like = db.session.query(Like).filter_by(author=userid, post_id=post_id).first()
                if curr_like:
                    db.session.delete(curr_like)
                else:
                    post.popularity += 1
                    db.session.add(post)
                db.session.add(curr_dislike)
                db.session.commit()
            disliked = True
    with app.app_context():
        numdislikes = Dislike.query.filter_by(post_id=post_id).count()
        numlikes = Like.query.filter_by(post_id=post_id).count()
    #return redirect(url_for('home'))
    return jsonify({"dislikes": numdislikes, "disliked": disliked, "likes": numlikes})

@app.route('/get_admin')
@is_authenticated
def get_admin():
    '''assign current user an admin role'''
    with app.app_context():
        userid = session.get('user').get('userinfo').get('sub')
        u = db.session.query(User).filter_by(id=userid).first()
        if u:
            role = db.session.query(Role).filter_by(name='admin').first()
            if role:
                user_roles = u.roles
                role_names = [role.name for role in user_roles]
                if 'admin' not in role_names:
                    u.roles.append(role)
                    db.session.commit()
    return redirect(url_for('home'))

@app.route('/admin_post')
@admin_required
def admin_dashboard():
    '''Admin dashboard to view and delete all posts'''
    posts = []
    with app.app_context():
        page = request.args.get('page', 1, type=int)
        all_posts = db.session.query(Post).order_by(Post.time.desc()).paginate(page=page,
                per_page=5)
    for i in all_posts.items:
        num_likes = Like.query.filter_by(post_id=i.id).count()
        num_dislikes = Dislike.query.filter_by(post_id=i.id).count()

        entry = {
                    'by': i.author,
                    'descendants': i.descendants,
                    'id': i.id,
                    'kids': i.kids,
                    'score': i.score,
                    'title': i.title,
                    'type': i.posttype,
                    'time': datetime.datetime.fromtimestamp(i.time),
                    'url': i.url,
                    'likes': num_likes,
                    'dislikes': num_dislikes
                }
        posts.append(entry)
    return render_template('admin_posts.html',title='Admin', posts=posts, page=page,
            pages=list(all_posts.iter_pages(left_edge=1, right_edge=1, left_current=1,
                right_current=2)))

@app.route('/admin_user')
@admin_required
def admin_user_dashboard():
    '''Admin dashboard to view and delete all users'''
    with app.app_context():
        all_users = User.query.all()

    return render_template('admin_users.html', title='Admin', users=all_users)

@app.route("/delete-user/<user_id>", methods=['GET'])
@admin_required
def delete_user(user_id):
    '''Request that handles the admin deleting the user'''
    with app.app_context():
        user_to_delete = db.session.get(User, user_id)
        db.session.delete(user_to_delete)
        db.session.commit()
    return redirect(url_for('admin_user_dashboard'))

@app.route("/delete-post/<post_id>", methods=['GET'])
@admin_required
def delete_post(post_id):
    '''Request that handles the admin deleting a post'''
    with app.app_context():
        post_to_delete = db.session.get(Post, post_id)
        db.session.delete(post_to_delete)
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.errorhandler(500)
def internal_error(error):
    '''Handles Internal Server Errors and logs it to error.txt'''
    with open('/home/olives/Hacker_News/errors.txt', 'a', encoding='utf-8') as file:
        file.write(traceback.format_exc())
    #print(traceback.format_exc(), file=open('/home/olives/Hacker_News/errors.txt', 'a'))
