#coding:utf-8
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField,SelectField,BooleanField,ValidationError
from wtforms.validators import Required,Length,Email,Regexp
from ..models import Role,User,Question
from flask_pagedown.fields import PageDownField

# class NameForm(FlaskForm):
#     name = StringField('What is your name?', validators=[Required()])
#     submit = SubmitField('--Submit--')

class EditProfileForm(FlaskForm):
    name = StringField(u'真实姓名',validators=[Length(0,62)])
    location = StringField(u'居住地', validators=[Length(0,64)])
    about_me = TextAreaField(u'关于我')
    submit = SubmitField(u'提交')

#管理员的资料啊编辑
class EditProfileAdminForm(FlaskForm):
    email = StringField(u'邮箱账号', validators=[Required(),Length(1,64),Email()])
    username = StringField(u'用户名', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          u'用户名必须包含至少一个字母, '
                                         u'数字、点或下划线')])
    confirmed =BooleanField(u'邮箱验证')
    role = SelectField(u'网站身份',coerce = int)
    name = StringField(u'真实姓名',validators=[Length(0,64)])
    location = StringField(u'居住地', validators=[Length(0,64)])
    about_me = TextAreaField(u'关于我')
    submit = SubmitField(u'提交')
    def __init__(self,user,*args,**kwargs):
        super(EditProfileAdminForm,self).__init__(*args,**kwargs)
        self.role.choices=[(role.id,role.name)
                           for role in Role.query.order_by(Role.name).all()]
        self.user=user

    def validate_username(self,field):
        if field.data!=self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError(u'用户名已存在')

    def validate_email(self,field):
        if field.data !=self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError(u'该邮箱已被注册')


#PageDownField富文本框
class QuestionForm(FlaskForm):
    body=PageDownField(u'你在想什么？',validators=[Required()])
    submit = SubmitField(u'提问')

class AnswerForm(FlaskForm):
    body=StringField('',validators=[Required()])
    submit=SubmitField(u'回答')


class SearchForm(FlaskForm):
    body=StringField(u'输入想要搜索的问题关键字',validators=[Required()])
    submit=SubmitField(u'搜索')