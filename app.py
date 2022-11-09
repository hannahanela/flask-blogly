"""Blogly application."""

from flask_debugtoolbar import DebugToolbarExtension
from flask import Flask, render_template, redirect, request, flash
from models import db, connect_db, User, Post, Tag, PostTag, DEFAULT_IMAGE_URL

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

app.config['SECRET_KEY'] = "SECRET!"
debug = DebugToolbarExtension(app)

connect_db(app)
db.create_all()


@app.get('/')
def homepage_index():
    """Show list of 5 most recent posts as homepage."""
    posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    
    return render_template("homepage.html", posts=posts)


################################################################################
# User routes

@app.get('/users')
def users_list():
    """Show list of users."""
    users = User.query.order_by('last_name', 'first_name').all()

    return render_template('users/list.html', users=users)


@app.get('/users/new')
def users_new_form():
    """Show form to create a new user."""
    return render_template("users/add-user.html")


@app.post('/users/new')
def users_new():
    """Handle form submission to create a new user."""
    first_name = request.form["first_name"]
    first_name = first_name if first_name else None
    last_name = request.form["last_name"]
    last_name = last_name if last_name else None
    img_url = request.form["img_url"]
    img_url = img_url if img_url else None

    if first_name == None or last_name == None:
        flash(f'Must provide a valid first and last name.')

        return redirect('/users/new')

    new_user = User(
        first_name=first_name,
        last_name=last_name,
        img_url=img_url,
    )

    db.session.add(new_user)
    db.session.commit()
    flash(f'User {new_user.full_name} added.')

    return redirect('/users')


@app.get('/users/<int:user_id>')
def users_detail(user_id):
    """Show details of a user."""
    user = User.query.get_or_404(user_id)

    return render_template('users/detail.html', user=user)


@app.get('/users/<int:user_id>/edit')
def users_edit_form(user_id):
    """Show form to edit a user."""
    user = User.query.get_or_404(user_id)

    return render_template('users/edit.html', user=user)


@app.post('/users/<int:user_id>/edit')
def users_edit(user_id):
    """Handle forms submission to edit a user."""
    user = User.query.get_or_404(user_id)
    user.first_name = request.form["first_name"]
    user.last_name = request.form["last_name"]
    img_url = request.form['img_url']
    img_url = img_url if img_url else DEFAULT_IMAGE_URL
    user.img_url = img_url

    db.session.add(user)
    db.session.commit()
    flash(f'User {user.full_name} edited.')

    return redirect("/users")


@app.post('/users/<int:user_id>/delete')
def users_delete(user_id):
    """Delete a user."""
    user = User.query.get_or_404(user_id)
    User.query.filter(User.id == user_id).delete()
    db.session.commit()
    flash(f'User {user.full_name} deleted.')

    return redirect('/users')


################################################################################
# Post routes

@app.get('/posts/<int:post_id>')
def posts_detail(post_id):
    """Show details of a post."""
    post = Post.query.get_or_404(post_id)
    post_tags = post.post_tag
    tag_ids = []

    for post_tag in post_tags:
        tag_ids.append(post_tag.tag_id)

    tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()

    return render_template('posts/detail.html', post=post, tags=tags)


@app.get('/users/<int:user_id>/posts/new')
def posts_new_form(user_id):
    """Show form to create a new post."""
    user = User.query.get_or_404(user_id)
    tags = Tag.query.all()

    return render_template("/posts/add-post.html", user=user, tags=tags)


@app.post('/users/<int:user_id>/posts/new')
def posts_new(user_id):
    """Handle form submission to create a new post."""
    title = request.form["title"]
    title = title if title else None
    content = request.form["content"]
    content = content if content else None
    tag_names = request.form.getlist('tags')

    if title == None or content == None:
        flash('Must provide valid title and content.')

        return redirect(f'/users/{user_id}/posts/new')

    new_post = Post(
        title=title,
        content=content,
        user_id=user_id
    )

    db.session.add(new_post)
    
    for name in tag_names:
        tag = Tag.query.filter_by(name=name).first()
        new_post.post_tag.append(PostTag(tag_id=tag.id))

    db.session.commit()
    flash(f'{new_post.title} successfully posted!')

    return redirect(f'/users/{user_id}')


@app.get('/posts/<int:post_id>/edit')
def posts_edit_form(post_id):
    """Show form to edit a post."""
    post = Post.query.get_or_404(post_id)
    tags = Tag.query.all()
    post_tags = post.post_tag
    tag_ids = []

    for post_tag in post_tags:
        tag_ids.append(post_tag.tag_id)

    selected_tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()

    return render_template(
        'posts/edit.html',
        post=post, tags=tags,
        selected_tags=selected_tags,
    )


@app.post('/posts/<int:post_id>/edit')
def posts_edit(post_id):
    """Handle form submission to edit a post."""
    post = Post.query.get_or_404(post_id)

    title = request.form["title"]
    content = request.form["content"]

    post.title = title
    post.content = content

    db.session.commit()
    flash(f'{post.title} successfully edited.')

    return redirect(f"/posts/{post_id}")


@app.post('/posts/<int:post_id>/delete')
def posts_delete(post_id):
    """Delete a post."""

    post = Post.query.get_or_404(post_id)
    user_id = post.user.id

    db.session.delete(post)
    db.session.commit()
    flash(f'{post.title} deleted.')

    return redirect(f'/users/{user_id}')


################################################################################
# Tag routes

@app.get('/tags')
def tags_list():
    """List all tags."""
    tags = Tag.query.order_by('name').all()

    return render_template('tags/list.html', tags=tags)


@app.get('/tags/<int:tag_id>')
def tags_detail(tag_id):
    """Show details of a tag."""
    # breakpoint()
    tag = Tag.query.get_or_404(tag_id)
    posts = tag.post_tag

    return render_template('tags/detail.html', tag=tag, posts=posts)


@app.get('/tags/new')
def tags_new_form():
    """Show form to create a new tag."""
    posts = Post.query.all()

    return render_template('tags/add-tag.html', posts=posts)


@app.post('/tags/new')
def tags_new():
    """Handle form submission and create a new tag."""
    name = request.form['name']
    name = name if name else None
    post_titles = request.form.getlist('posts')

    if name == None:
        flash('Must provide a tag name.')

        return redirect('/tags/new')

    new_tag = Tag(name=name)

    db.session.add(new_tag)

    for title in post_titles:
        # Post titles are currently not unique, so not guaranteed accurate fetch
        post = Post.query.filter_by(title=title).first()
        new_tag.post_tag.append(PostTag(post_id=post.id))

    db.session.commit()
    flash(f'{new_tag.name} created')

    return redirect('/tags')


@app.get('/tags/<int:tag_id>/edit')
def tags_edit_form(tag_id):
    """Show form to edit a tag."""
    tag = Tag.query.get_or_404(tag_id)
    posts = Post.query.all()
    post_tags = tag.post_tag
    post_ids = []

    for post_tag in post_tags:
        post_ids.append(post_tag.post_id)

    selected_posts = Post.query.filter(Post.id.in_(post_ids)).all()

    return render_template(
        '/tags/edit.html',
        tag=tag,
        posts=posts,
        selected_posts=selected_posts,
    )


@app.post('/tags/<int:tag_id>/edit')
def tags_edit(tag_id):
    """Handle form submission to edit a tag."""
    tag = Tag.query.get_or_404(tag_id)

    tag.name = request.form['name']

    db.session.commit()
    flash(f'{tag.name} edited')

    return redirect('/tags')


@app.post('/tags/<int:tag_id>/delete')
def tags_delete(tag_id):
    """Delete a tag."""
    # currently handles only 1 instance of both PostTag and Post
    tag = Tag.query.get_or_404(tag_id)
    post_tag = tag.post_tag[0]
    post_id = tag.post_tag[0].post_id
    post = Post.query.get_or_404(post_id)
    post.post_tag.remove(post_tag)

    db.session.delete(post_tag)
    db.session.delete(tag)
    db.session.commit()
    flash(f'{tag.name} deleted')

    return redirect('/tags')
