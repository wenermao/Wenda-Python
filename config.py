#coding:utf-8
#配置
import os
besedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # csrf攻击
    SECRET_KEY = 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS  = False
    FLASKY_MAIL_SUBJECT_PREFIX = '[Wenda]'
    FLASKY_MAIL_SENDER = '1432914530@qq.com'
    FLASKY_ADMIN= os.environ.get('FLASKY_ADMIN')
    FLASKY_QUESTIONS_PER_PAGE = 20
    FLASKY_ANSWERS_PER_PAGE=30
    FLASKY_FOLLOWERS_PER_PAGE = 40
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG =True
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_POST = 587
    MAIL_USE_TLS = True
    # MAIL_USERNAME = '1432914530@qq.com'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@127.0.0.1/testD'
#数据库没写
class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@127.0.0.1/testP'

#单元测试的都没写
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@127.0.0.1/testT'
config = {
    'development':DevelopmentConfig,
    'production':ProductionConfig,
    'testing':TestingConfig,
    'default':DevelopmentConfig
}