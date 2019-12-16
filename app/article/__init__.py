# -*- coding: utf-8 -*-
# @Author: wangchao
# @Time: 19-12-4 下午3:44
from flask import Blueprint
from flask_restful import Api

from app.models import Permission

article = Blueprint('article', __name__)

# 循环引用
from app.article import views


