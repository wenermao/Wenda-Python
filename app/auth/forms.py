#coding:utf-8
#登录表单
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField,SubmitField
from wtforms.validators import Required, Length, Email,Regexp,EqualTo
from wtforms import ValidationError
from ..models import User
class LoginForm(FlaskForm):
    email = StringField(u'邮箱账号', validators=[Required(),Length(1,64),Email()])
    password = PasswordField(u'密码', validators=[Required()])
    remember_me = BooleanField(u'点我记录登录')
    submit = SubmitField(u'登录')

class RegistrationForm(FlaskForm):
    email = StringField(u'邮箱账号',validators=[Required(),Length(1,64),Email()])
    username = StringField(u'用户名', validators=[Required(),Length(1,64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                                                                     u'用户名必须以字母开头，并包含至少一个 '
                                                                                     u'数字、点或下划线（非中文）')])
    password = PasswordField(u'密码',validators=[Required(),EqualTo('password2', message=u'两次密码必须相同')])
    password2 = PasswordField(u'确认密码', validators=[Required()])
    submit = SubmitField(u'注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(u'该邮箱已被注册')
    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(u'用户名已存在')

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(u'原密码  Old password', validators=[Required()])
    password = PasswordField(u'新密码  New password', validators=[Required(),EqualTo('password2', message=u'两次密码必须相同')])
    password2 = PasswordField(u'确认密码  Confirm Password', validators=[Required()])
    submit = SubmitField(u'确认密码')