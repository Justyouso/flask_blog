# -*- coding: utf-8 -*-
# @Author: wangchao
# @Time: 19-6-4 下午4:58
from flask import render_template
from flask_mail import Message

from app import mail
from config import Config


# 邮件发送
def send_mail(to, subject, template, **kwargs):
    msg = Message(Config.FLASKY_MAIL_SUBJECT_PREFIX + subject,
                  sender=Config.FLASKY_MAIL_SENDER, recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    # msg.html = render_template(template + '.html', **kwargs)
    mail.send(msg)
