# -*- coding: utf-8 -*-
# @Author: wangchao
# @Time: 19-6-4 下午4:57

from flask import render_template, abort, flash, redirect, url_for
from flask_login import current_user, login_required

from app import db
from app.main import main
from app.main.forms import EditProfileForm, EditProfileAdminForm
from app.models import User, Role
from app.decorators import admin_required


@main.route("/")
def index():
    return render_template('index.html')


@main.route("/user/<username>")
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    return render_template('user.html', user=user)


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
