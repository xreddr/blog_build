from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from sqlalchemy import desc
from werkzeug.exceptions import abort
from .auth import login_required
from ..models import db, User, Post
import datetime

bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    posts = Post.query.order_by(desc(Post.timestamp)).all()
    return render_template('blog/index.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        new_title = request.form['title']
        new_body = request.form['body']
        error = None

        if not new_title:
            error = 'Title is required.'

        if not new_body:
            error = 'Body is required.'

        if error is not None:
            flash(error)

        else:
            p = Post(
                title=new_title,
                body=new_body,
                timestamp=datetime.datetime.utcnow(),
                user_id=g.user.id
            )
            db.session.add(p)
            db.session.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


def get_post(id, check_author=True):
    post = Post.query.get_or_404(id)
    if check_author and post.user_id != g.user.id:
        abort(403)
    return post


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        up_title = request.form['title']
        up_body = request.form['body']
        error = None

        if not up_title:
            error = 'Title is required.'

        if not up_body:
            error = 'Body is required.'

        if error is not None:
            flash(error)

        else:
            post.title = up_title
            post.body = up_body
            db.session.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    post = get_post(id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('blog.index'))
