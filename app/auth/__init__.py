# -*- coding: utf-8 -*-
# @Author: wangchao
# @Time: 19-6-6 上午10:32
from flask import Blueprint

auth = Blueprint('auth', __name__)
from app.auth import views
