#coding:utf-8
#route装饰器定义认证路由相关

from flask import render_template, redirect,request,url_for,flash
from flask_login import login_user, logout_user, login_required, \
    current_user
from . import auth
from ..models import User
from .forms import LoginForm, RegistrationForm, ChangePasswordForm
from .. import db
from ..email import send_email

@auth.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user,form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash(u'用户名或密码错误')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash(u'退出登录成功！')
    return redirect(url_for('main.index'))
#设置时间
@auth.route('/register',methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username = form.username.data,
                    password = form.password.data,)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email,u'验证邮箱',
                   'auth/email/confirm',user=user,token = token)

        flash(u'账户激活邮件已发送至您的邮箱，请注意查收。')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        # user = User(confirmed=1)
        # db.session.update(user)
        # db.session.commit()
        flash(u'恭喜成功激活邮箱！')
    else:
        flash(u'激活链接错误或已过期，请点击重新发送。')
    return redirect(url_for('main.index'))
#处理没有邮件确认账户的登录情况
@auth.before_app_request
def before_request():
    if current_user.is_authenticated and not current_user.confirmed\
        and request.endpoint[:5] != 'auth.' and request.endpoint !='static':
        return redirect(url_for('auth.unconfirmed'))
@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')
#重新发送确认邮件
@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, u'验证邮箱',
                   'auth/email/confirm',user=current_user,token = token)
    flash(u'账户激活邮件已发送至您的邮箱，请注意查收。')
    return redirect(url_for('main.index'))


@auth.route('/change-password', methods=['GET','POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        #原密码匹配
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash(u'密码更新成功')
            return redirect(url_for('main.index'))
        else:
            flash(u'原密码错误')
    return render_template("auth/change_password.html", form = form)

#更新最近登录时间
@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed and request.endpoint[:5]!='auth.':
            return redirect(url_for('auth.unconfirmed'))


