# -*- coding: utf-8 -*-
# @Author: wangchao
# @Time: 19-6-4 下午4:57
from flask import Blueprint
from flask_restful import Api

from app.models import Permission

main = Blueprint('main', __name__)

# 循环引用
from app.main import views, errors


# api = Api(main)

# 将Permission定义到全局上下文中,前端html模板可以直接使用
@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
