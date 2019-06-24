# -*- coding: utf-8 -*-
# @Author: wangchao
# @Time: 19-6-4 下午4:57

from flask import render_template,abort
from app.main import main
from app.models import User


@main.route("/")
def index():
    return render_template('index.html')


@main.route("/user/<username>")
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    return render_template('user.html',use=user)