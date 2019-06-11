# -*- coding: utf-8 -*-
# @Author: wangchao
# @Time: 19-6-4 下午4:57
from flask import Blueprint
from flask_restful import Api

main = Blueprint('main', __name__)

# 循环引用
from app.main import views, errors
# api = Api(main)
