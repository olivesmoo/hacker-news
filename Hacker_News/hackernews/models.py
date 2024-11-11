'''SQLite db models'''
from hackernews import db

class User(db.Model):
    '''Model for a user'''
    id = db.Column(db.String, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file =  db.Column(db.String(120), nullable=False, default='default.jpg')
    likes = db.relationship('Like', backref='user', cascade='all, delete-orphan')
    dislikes = db.relationship('Dislike', backref='user', cascade='all, delete-orphan')
    roles = db.relationship('Role', secondary='user_roles')
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Post(db.Model):
    '''Model for a post'''
    author = db.Column(db.String(100), nullable=False)
    descendants = db.Column(db.Integer)
    id = db.Column(db.Integer, primary_key=True)
    kids = db.Column(db.PickleType)
    score = db.Column(db.Integer)
    title = db.Column(db.String(100), nullable=False)
    posttype = db.Column(db.String(100))
    time = db.Column(db.Integer)
    url = db.Column(db.String, nullable=False)
    likes = db.relationship('Like', backref='post', cascade='all, delete-orphan')
    dislikes = db.relationship('Dislike', backref='post', cascade='all, delete-orphan')
    popularity = db.Column(db.Integer, default=0)
    def increase_popularity(self):
        '''increase the popularity of a post by 1 (likes + dislikes)'''
        self.popularity += 1
        db.session.commit()
    def decrease_popularity(self):
        '''decrease the popularity of a post by 1 (likes+dislikes)'''
        if self.popularity > 0:
            self.popularity -= 1
            db.session.commit()

class Role(db.Model):
    '''Model for a user Role'''
    __tablename__='roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)
    def __repr__(self):
        return f"Role('{self.id}', '{self.name}')"

class UserRoles(db.Model):
    '''Relational table for users and roles'''
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))
    def __repr__(self):
        return f"UserRole('{self.user_id}', '{self.role_id}')"

class Like(db.Model):
    '''Model for all likes'''
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete="CASCADE"), nullable=False)
    def __repr__(self):
        return f"Like('{self.author}', '{self.post_id}')"

class Dislike(db.Model):
    '''Model for all dislikes'''
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete="CASCADE"), nullable=False)
    def __repr__(self):
        return f"Dislike('{self.author}', '{self.post_id}')"
