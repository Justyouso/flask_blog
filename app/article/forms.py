# -*- coding: utf-8 -*-
# @Author: wangchao
# @Time: 19-6-4 下午4:57
from flask_wtf import FlaskForm
from flask_pagedown.fields import PageDownField
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, \
    SelectField,HiddenField
from wtforms.validators import Length, DataRequired, Email, Regexp, \
    ValidationError
from app.models import Role,User


# 编辑个人信息
class EditProfileForm(FlaskForm):
    name = StringField('姓名', validators=[Length(0, 64)])
    location = StringField('地区', validators=[Length(0, 64)])
    about_me = TextAreaField('关于我')
    submit = SubmitField('提交')


class EditProfileAdminForm(FlaskForm):
    email = StringField('邮箱',
                        validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('昵称',
                           validators=[DataRequired(), Length(1, 64),
                                       Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                              '用户名必须只有字母，数字、点或下划线')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('权限', coerce=int)
    name = StringField('姓名', validators=[Length(0, 64)])
    location = StringField('地区', validators=[Length(0, 64)])
    about_me = TextAreaField('关于我')
    submit = SubmitField('提交')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in
                             Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(
                email=field.data).first():
            raise ValidationError('邮箱已被注册')

    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(
                username=field.data).first():
            raise ValidationError('用户名已被使用')


from wtforms.widgets.core import TextArea


class MyTextArea(TextArea):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __call__(self, field, **kwargs):
        for arg in self.kwargs:
            if arg not in kwargs:
                kwargs[arg] = self.kwargs[arg]
        return super(MyTextArea, self).__call__(field, **kwargs)


class ArticlesForm1(FlaskForm):
    """
    文章
    """
    title = PageDownField("标题", validators=[DataRequired()])
    body = PageDownField("正文", validators=[DataRequired()],
                         )
    submit = SubmitField('提交')


class ArticlesForm(FlaskForm):
    """
    文章
    """
    body = TextAreaField("正文", validators=[DataRequired()],)
    title = TextAreaField("标题", validators=[DataRequired()],)
    submit = SubmitField('提交')


class CommentForm(FlaskForm):
    """
    评论
    """
    body = StringField('', validators=[DataRequired()])
    submit = SubmitField('提交')
