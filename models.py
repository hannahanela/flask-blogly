"""Models for Blogly."""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey

db = SQLAlchemy()
DEFAULT_IMAGE_URL = "https://picsum.photos/id/237/200/300"


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)


class User(db.Model):
    """User class that includes an id, the user's first name, last name,
    and an image url"""

    __tablename__ = "users"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)

    first_name = db.Column(db.String(50),
                           nullable=False)

    last_name = db.Column(db.String(50),
                          nullable=False)

    img_url = db.Column(db.String,
                        nullable=False,
                        default=DEFAULT_IMAGE_URL)

    posts = db.relationship('Post', backref='user')

    def get_full_name(self):
        """Generate user's full name."""

        return f'{self.first_name} {self.last_name}'



class Post(db.Model):
    """Post class that includes an post id, the post's title, content,
    date-created-at timestamp, and a user-id"""

    __tablename__ = "posts"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)

    title = db.Column(db.String(100),
                      nullable=False)

    content = db.Column(db.String(1500),
                        nullable=False)

    created_at = db.Column(db.DateTime,
                           nullable=False,
                           default=db.func.now())

    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id'),
                        nullable=False)

    post_tag = db.relationship('PostTag',
                               backref='post')


class Tag(db.Model):
    """Tag class that includes an tag id and tag name"""

    __tablename__ = "tags"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)

    name = db.Column(db.String(20),
                     nullable=False,
                     unique=True)

    post_tag = db.relationship('PostTag',
                               backref='tag')


class PostTag(db.Model):
    """PostTag class that includes a foreign post_id and a foreign tag_id"""

    __tablename__ = "post_tags"

    post_id = db.Column(db.Integer,
                        db.ForeignKey('posts.id'),
                        nullable=False,
                        primary_key=True)

    tag_id = db.Column(db.Integer,
                       db.ForeignKey('tags.id'),
                       nullable=False,
                       primary_key=True)
