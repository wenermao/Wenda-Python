#coding:utf-8
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_moment import Moment
#数据库
from flask_sqlalchemy import SQLAlchemy
#mail
from flask_mail import Mail
from config import config
#登录用
from flask_login import LoginManager
from flask_pagedown import PageDown




bootstrap = Bootstrap()
#时间
moment = Moment()
#数据库
db = SQLAlchemy()
#mail
mail = Mail()
#login
login_manager = LoginManager()
login_manager.session_protection = 'strong'
#登录路由在蓝本中，所以加上蓝本名字
login_manager.login_view = 'auth.login'
#提问的富文本框
pagedown=PageDown()

#工厂函数
def create_app(config_name):
    app = Flask(__name__)
    #导入config配置
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)

    #附加路由、错误页面蓝本
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    #附加蓝本auth用户认证，url_prefix是自动加个前缀
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')




    return app
