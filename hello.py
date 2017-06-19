#coding:utf-8
#初始化
import os
#session, redirect, url_for用于重定向的
from flask import Flask, render_template, session, redirect, url_for, flash
from flask_script import Manager, Shell
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Required
#数据库
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate,MigrateCommand
besedir = os.path.abspath(os.path.dirname(__file__))
#mail
from flask_mail import Mail, Message
from threading import Thread
app = Flask(__name__)
#csrf攻击
app.config['SECRET_KEY'] = 'hard to guess string'
#数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@127.0.0.1/test'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#邮箱
app.config['MAIL_SERVER']='smtp.qq.com'
app.config['MAIL_POST'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = '1432914530@qq.com'
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
# app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
# app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] ='[Flasky]'
app.config['FLASKY_MAIL_SENDER'] = '1432914530@qq.com'
app.config['FLASKY_ADMIN'] = '1432914530@qq.com'
#app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')


manager = Manager(app)
bootstrap = Bootstrap(app)
#时间
moment = Moment(app)
#数据库
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)
#mail
mail = Mail(app)

class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('--Submit--')


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64),unique=True)
    users = db.relationship('User', backref = 'role', lazy='dynamic')
    def __repr__(self):
        return '<Role %r>' %self.name

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64),unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    def __repr__(self):
        return '<User %r>' %self.username




# #路由和视图
# @app.route('/')
# #视图函数
# def index():
#     return '<h1>Hello World</h1>'
#
# #动态名字
# @app.route('/user/<name>')
# def user(name):
#     return '<h1>Hello %s!</h1>' % name

@app.route('/', methods=['GET', 'POST'])
def index():
    name = None
    form = NameForm()
    if form.validate_on_submit():
        user =User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username = form.name.data)
            db.session.add(user)
            session['known'] = False
            #email
            if app.config['FLASKY_ADMIN']:
                send_email(app.config['FLASKY_ADMIN'], 'New User', 'mail/new_user', user=user)
        else:
            session['known'] = True
        form.name.data=''
        return redirect(url_for('index'))

        # #根据上一次输入的判断是否为老用户
        # old_name = session.get('name')
        # if old_name is not None and old_name!=form.name.data:
        #     flash('looks like you have changed your name')
        # session['name'] = form.name.data
        # return redirect(url_for('index'))

        # name = form.name.data
        # form.name.data = ''

    return render_template('index.html', form = form, name = session.get('name'), known=session.get('known', False), current_time=datetime.utcnow())

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'),500



def make_shell_context():
    return dict(app=app, db=db,User=User,Role=Role)
manager.add_command("shell",Shell(make_context=make_shell_context))

#send email
#异步
def send_async_email(app,msg):
    with app.app_context():
        mail.send(msg)
def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX']+subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body=render_template(template+'.txt',**kwargs)
    msg.html = render_template(template+'.html',**kwargs)
    # mail.send(msg)
    thr = Thread(target=send_async_email, args=[app,msg])
    thr.start()
    return thr




#启动服务器
if __name__ == '__main__':
    db.create_all()
    # manager.run()
    app.run()
    #debug=True:debug模式