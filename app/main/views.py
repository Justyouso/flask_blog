# -*- coding: utf-8 -*-
# @Author: wangchao
# @Time: 19-6-4 下午4:57

from flask import render_template,abort,flash,redirect,url_for
from app.main import main
from app.models import User
from app.main.forms import EditProfileForm
from flask_login import current_user,login_required
from app import db


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
