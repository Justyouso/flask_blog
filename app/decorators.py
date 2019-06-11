# -*- coding: utf-8 -*-
# @Author: wangchao
# @Time: 19-6-11 下午10:26
from functools import wraps
from flask import abort
from flask_login import current_user
from app.models import Permission


# 权限验证
def permissions_required(permission):
    def decorators(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)

        return decorated_function

    return decorators


# 验证管理员权限
def admin_required(f):
    # 先传permission,再传f
    return permissions_required(Permission.ADMINISTER)(f)
