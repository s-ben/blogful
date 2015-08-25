from flask import render_template

from blog import app
from .database import session
from .models import Post

import mistune
from flask import request, redirect, url_for

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
    
    posts = session.query(Post).get(post_id)  
    return render_template("post.html", posts=posts)




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
    
    posts = session.query(Post).get(post_id)
    
    # request.form["title"] = posts.title
    # request.form["content"] = posts.content
    return render_template("edit_post.html", posts=posts)

@app.route("/post/<int:post_id>/edit", methods=["POST"])
def edit_post_post(post_id=1):
    
    post = session.query(Post).get(post_id)
    post.title = request.form["title"]
    post.content = content=mistune.markdown(request.form["content"])
    

    session.commit()
    return redirect(url_for('post', post_id=post.id))  
    

@app.route("/post/add", methods=["GET"])
def add_post_get():
    return render_template("add_post.html")
    
@app.route("/post/add", methods=["POST"])
def add_post_post():
    post = Post(
        title=request.form["title"],
        content=mistune.markdown(request.form["content"]),
    )
    session.add(post)
    session.commit()
    return redirect(url_for("posts"))