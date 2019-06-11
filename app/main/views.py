# -*- coding: utf-8 -*-
# @Author: wangchao
# @Time: 19-6-4 下午4:57

from flask import render_template
from app.main import main


@main.route("/")
def index():
    return render_template('index.html')