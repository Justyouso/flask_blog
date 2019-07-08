# -*- coding: utf-8 -*-
# @Author: wangchao
# @Time: 19-6-4 下午4:57

from flask import render_template, abort, flash, redirect, url_for, request, \
    current_app
from flask_login import current_user, login_required

from app import db
from app.main import main
from app.main.forms import EditProfileForm, EditProfileAdminForm,PostForm
from app.models import User, Role, Permission, Post
from app.decorators import admin_required


@main.route("/", methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():
        post = Post(body=form.body.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()) \
        .paginate(page, per_page=current_app.config["FLASKY_POSTS_PER_PAGE"],
                  error_out=False)
    posts = pagination.items
    return render_template('index.html', form=form, posts=posts,
                           pagination=pagination)


@main.route("/user/<username>")
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html', user=user, posts=posts)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    data = {"title": "编辑个人信息", "h": "编辑个人信息", }
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('你的个人信息已经更新')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('auth/common.html', form=form, data=data)


@main.route('/edit-profile/<int:id>', methods=['GET','POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    """
    管理员修改个人信息
    :param id: 用户ID
    :return: html
    """
    data = {"title": "编辑个人信息", "h": "编辑个人信息", }
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('个人信息已修改')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('auth/common.html', form=form, user=user, data=data)


@main.route('/post/<int:id>')
def post(id):
    """
    文章详情
    :param id: 文章ID
    :return: HTML
    """
    post = Post.query.get_or_404(id)
    return render_template('post.html', posts=[post])


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and not current_user.can(
            Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.bady = form.body.data
        db.session.add(post)
        flash('文章已修改')
        return redirect((url_for('post', id=post.id)))
    form.body.data = post.body
    return render_template('edit_post.html', form=form)
