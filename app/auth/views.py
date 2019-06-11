# -*- coding: utf-8 -*-
# @Author: wangchao
# @Time: 19-6-6 上午10:33
from flask import render_template, redirect, request, url_for, flash
from flask_login import current_user
from flask_login import login_user, login_required, logout_user

from app import db
from app.auth import auth
from app.auth.forms import LoginForm, RegistrationForm, UpdatePasswordForm, \
    EmailForm, ResetPasswordForm
from app.email import send_mail
from app.models import User


@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get("next") or url_for('main.index'))
        flash("invalid username or password")
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash("you have been logged out.")
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_mail(user.email, '验证账号', 'auth/email/confirm', user=user,
                  token=token)
        flash('验证码已发送到邮箱')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)


# 验证
@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))


@auth.before_app_request
def before_request():
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.endpoint[:5] != 'auth.' \
            and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


# 重新验证
@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_mail(current_user.email, 'Confirm Your Account', 'auth/email/confirm',
              user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))


# 修改密码
@auth.route('/password/update', methods=['GET', 'POST'])
@login_required
def update_password():
    form = UpdatePasswordForm()
    if form.validate_on_submit():
        old_password = form.old_password.data
        if current_user.verify_password(old_password):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            return redirect(url_for('main.index'))
        else:
            flash('密码不正确')
    return render_template('auth/updatepwd.html', form=form)


# 重置密码(邮箱验证)
@auth.route('/password/reset', methods=['GET', 'POST'])
def reset_password():
    data = {"title": "RESET PWD EMAIL", "h": "RESET PWD EMAIL"}
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None:
            user.password = form.password.data
            user.confirmed = False
            token = user.generate_confirmation_token()
            send_mail(form.email.data, '密码重置',
                      'auth/email/confirm', token=token,user=user)
            flash('验证码已发送到邮箱')
            return redirect(url_for('main.index'))
    return render_template('auth/common.html', form=form, data=data)
