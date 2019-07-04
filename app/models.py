# -*- coding: utf-8 -*-
# @Author: wangchao
# @Time: 19-6-4 下午4:58
from datetime import datetime
from flask_login import UserMixin, AnonymousUserMixin
from flask import current_app,request
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from app import db
from app import login_manager
import hashlib


# flask_login的回调函数
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# 角色
class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role % r>' % self.name

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0Xff, False)
        }

        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow,
                             verbose_name="记住时间")
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow,
                          verbose_name="登录时间")
    avatar_hash = db.Column(db.String(32), verbose_name="头像")
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User % r>' % self.username

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        """
        设置密码
        :param password: 密码
        :return: 
        """
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """
        验证密码
        :param password: 密码
        :return: bool
        """
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        """
        生成token
        :param expiration: 有效时间
        :return: str
        """
        s = Serializer(current_app.config["SECRET_KEY"], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        """
        账号验证
        :param token: token
        :return: bool
        """
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token)
        except Exception as e:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        # 给用户赋予角色
        self.test = 1
        if self.role is None:
            # 若email是管理员的邮箱则赋予管理员角色
            if self.email == current_app.config['ADMIN'][0]:
                self.role = Role.query.filter_by(permissions=0xff).first()
            else:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()

    def can(self, permissions):
        """
        角色验证
        :param permissions: 权限(int)
        :return: bool
        """
        # 进行and运算再对比验证
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        """
        管理员权限
        :return: bool
        """
        return self.can(Permission.ADMINISTER)

    def ping(self):
        """
        用户一登录就写入登录时间
        :return: 
        """
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def gravatar(self, size=100, default='identicon', rating='g'):
        """
        生成头像
        :param size: 图片大小(像素)
        :param default: 默认图片生成方式
        :param rating: 图片级别
        :return: URL
        """
        if request.is_secure:
            url = 'https://secure.gravatar.com/avator'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        params = {
            "url": url,
            "hash": hash,
            "size": size,
            "default": default,
            "rating": rating
        }
        return '{url}/hash?s={size}&d={default}&r={rating}'.format(**params)

    @staticmethod
    def generate_fake(count=100):
        """
        生成假用户
        :param count: 数量
        :return: 
        """
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     confirmed=True,
                     name=forgery_py.name.full_name(),
                     location=forgery_py.address.city(),
                     about_me=forgery_py.lorem_ipsum.sentence(),
                     member_since=forgery_py.date.date(True)
                     )
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True,
                          default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(
                randint(0, user_count - 1)).first()
            p = Post(body=forgery_py.lorem_ipsum.sentences(
                randint(1, 3)),
                timestamp=forgery_py.date.date(True),
                author=u)
            db.session.add(p)
            db.session.commit()


# 匿名用户没有权限(未登录的都属于匿名用户)
class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


# 管理匿名用户
login_manager.anonymous_user = AnonymousUser




