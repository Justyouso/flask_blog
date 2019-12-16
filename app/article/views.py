# -*- coding: utf-8 -*-
# @Author: wangchao
# @Time: 19-12-4 下午3:46

from flask import render_template, abort, flash, redirect, url_for, request, \
    current_app, make_response
from flask_login import current_user, login_required
from app.models import User, Role, Permission, Post, Comment
from app.article import article
from app import db
from app.article.forms import ArticlesForm, CommentForm


# 创建文章
@article.route("/create", methods=['GET', 'POST'])
def article_create():
    form = ArticlesForm()
    # 权限验证和表单验证
    if current_user.can(Permission.WRITE_ARTICLES):
        if form.validate_on_submit():
            body_html = request.form['fancy-editormd-html-code']
            title_html = "<h1>" + form.title.data + "</h1>"
            post = {
                "body": form.body.data,
                "body_html": body_html,
                "title": form.title.data,
                "title_html": title_html,
                "author": current_user._get_current_object()
            }
            post = Post(**post)
            db.session.add(post)
            return redirect(url_for('main.index'))
        else:
            return render_template('article/post_create.html', form=form)
    return redirect(url_for("auth.login"))


@article.route("/create/display", methods=['GET', 'POST'])
def article_create_display():
    form = ArticlesForm()
    if current_user.can(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():
        post = Post(body=form.body.data,
                    title=form.title.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('main.index'))

    return render_template('article/post_create_display.html', form=form)


# 文章详情
@article.route('/<int:id>', methods=['GET', 'POST'])
def article_detail(id):
    """
    文章详情
    :param id: 文章ID
    :return: HTML
    """
    post = Post.query.get_or_404(id)
    # 提交评论
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        flash('评论已发布')
        return redirect(url_for('.article_detail', id=post.id, page=-1))

    # 文章详情
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) / current_app.config[
            'FLASKY_COMMENTS_PRE_PAGE'] + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PRE_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('article/post_list.html', posts=[post], form=form,
                           comments=comments, pagination=pagination)


@article.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def article_edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and not current_user.can(
            Permission.ADMINISTER):
        abort(403)
    form = ArticlesForm()
    if form.validate_on_submit():
        post.body = form.body.data
        post.title = form.title.data
        db.session.add(post)
        flash('文章已修改')
        return redirect(url_for('.article_detail', id=post.id))
    form.body.data = post.body
    return render_template('article/post_edit.html', form=form)
