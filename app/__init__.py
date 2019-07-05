# -*- coding: utf-8 -*-
# @Author: wangchao
# @Time: 19-6-4 下午4:59


from flask import Flask
from flask_pagedown import PageDown
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import import_string

from config import config
# from .main import main as main_bule

blueprints = [
    "app.main:main",
    "app.auth:auth"
]
bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
# 实现客户端Markdown到HTML的转换程序
pagedown = PageDown()

login_manager = LoginManager()
# 登录安全配置(当客户端IP和浏览器用户代理信息发生异常时,登出用户)
login_manager.session_protection = 'strong'
# 设置登录页端点
login_manager.login_view = 'auth.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)

    # 注册蓝本
    # app.register_blueprint(main_bule)
    for bp_name in blueprints:
        bp = import_string(bp_name)
        app.register_blueprint(bp, url_prefix="/" + bp_name.split(":")[1])
    # 附加路由和自定义的错误页面
    return app
