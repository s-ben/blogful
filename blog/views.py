from flask import render_template

from blog import app
from .database import session
from .models import Post

import mistune
from flask import request, redirect, url_for

from flask import flash
from flask.ext.login import login_user, current_user, logout_user
from werkzeug.security import check_password_hash
from .models import User

from flask.ext.login import login_required

from werkzeug.security import generate_password_hash

# @app.route("/")
# def posts():
#     posts = session.query(Post)
#     posts = posts.order_by(Post.datetime.desc())
#     posts = posts.all()
#     return render_template("posts.html",
#         posts=posts
#     )

@app.route("/")
@app.route("/page/<int:page>")
def posts(page=1, paginate_by=10):
    # Zero-indexed page
    page_index = page - 1

    count = session.query(Post).count()

    start = page_index * paginate_by
    end = start + paginate_by

    total_pages = (count - 1) / paginate_by + 1
    has_next = page_index < total_pages - 1
    has_prev = page_index > 0

    posts = session.query(Post)
    posts = posts.order_by(Post.datetime.desc())
    posts = posts[start:end]

    return render_template("posts.html",
        posts=posts,
        has_next=has_next,
        has_prev=has_prev,
        page=page,
        total_pages=total_pages
    )

@app.route("/post/<int:post_id>")
def post(post_id=1):
    
    post = session.query(Post).get(post_id)  
    return render_template("post.html", post=post)




@app.route("/post/<int:post_id>/delete", methods=["GET"])
def delete_post_get(post_id=1):
    
    post = session.query(Post).get(post_id)

    # request.form["title"] = posts.title
    # request.form["content"] = posts.content
    # return render_template("edit_post.html", posts=posts)
    return render_template("confirm_delete.html", posts=posts)


@app.route("/post/<int:post_id>/delete", methods=["POST"])
def delete_post_post(post_id=1):
    
    post = session.query(Post).get(post_id)
    deleted = False
    if request.form["delete_button"] == "Yes":
        # return redirect(url_for('post', post_id=post.id))  
        
        
        session.delete(post)
        session.commit()
        # return redirect(url_for("posts"))
        deleted = True
    else:
        pass
    # Response = request.form["value"]
        # return redirect(url_for('post', post_id=post.id))  
    
    # request.form["title"] = posts.title
    # request.form["content"] = posts.content
    # return render_template("edit_post.html", posts=posts)
    if deleted:
        return redirect(url_for("posts"))
    else:
        return redirect(url_for('post', post_id=post.id))  

@app.route("/post/<int:post_id>/edit", methods=["GET"])
def edit_post_get(post_id=1):
    
    post = session.query(Post).get(post_id)
    
    if (post.author_id == current_user.id):
        return render_template("edit_post.html", post=post)
    else:
        return redirect(url_for('post', post_id=post.id))  
    
    # request.form["title"] = posts.title
    # request.form["content"] = posts.content
    

@app.route("/post/<int:post_id>/edit", methods=["POST"])
def edit_post_post(post_id=1):
    
    post = session.query(Post).get(post_id)
    post.title = request.form["title"]
    post.content = content=mistune.markdown(request.form["content"])
    

    session.commit()
    return redirect(url_for('post', post_id=post.id))  
    

@app.route("/post/add", methods=["GET"])
@login_required
def add_post_get():
    return render_template("edit_post.html")
    
@app.route("/post/add", methods=["POST"])
@login_required
def add_post_post():
    post = Post(
        title=request.form["title"],
        content=mistune.markdown(request.form["content"]),
        author=current_user
    )

    session.add(post)
    session.commit()
    return redirect(url_for("posts"))
    

@app.route("/add_user", methods=["GET"])
def add_user_get():
    return render_template("add_user.html")

@app.route("/add_user", methods=["POST"])
def add_user_post():
    name = request.form["name"]
    email = request.form["email"]
    password = request.form["password"]
    
    if session.query(User).filter_by(email=email).first():
        print "User with that email address already exists"
        return
    
    user = User(name=name, email=email, password=generate_password_hash(password))
    session.add(user)
    session.commit()

    login_user(user)
    
    return redirect(request.args.get('next') or url_for("posts"))
    
    

@app.route("/login", methods=["GET"])
def login_get():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login_post():
    email = request.form["email"]
    password = request.form["password"]
    user = session.query(User).filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        flash("Incorrect username or password", "danger")
        return redirect(url_for("login_get"))

    login_user(user)
    return redirect(request.args.get('next') or url_for("posts"))
    

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(request.args.get('next') or url_for("posts"))