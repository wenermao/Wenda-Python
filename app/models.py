#coding:utf-8
#数据库模型
from . import db
#密码
from werkzeug.security import generate_password_hash,check_password_hash
#登录模型
from flask_login import UserMixin, AnonymousUserMixin
#关于确认账户
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from . import login_manager
from datetime import datetime
from markdown import markdown
import bleach


class Permission:
    FOLLOW=0x01  #关注
    ANSWER=0x02  #回答
    ASK=0x04  #提问
    MODERATE_ANSWER=0x08  #管理回答
    ADMINISTER=0x80  #超管权限


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64),unique=True)
    default = db.Column(db.Boolean,default=False,index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref = 'role', lazy='dynamic')
    #权限 普通用户(注册就是了，协管员，超管
    @staticmethod
    def insert_roles():
        roles={
            'User':(Permission.FOLLOW|
                    Permission.ASK|
                    Permission.ANSWER, True),
            'Moderator':(Permission.FOLLOW|
                         Permission.ASK|
                         Permission.ANSWER|
                         Permission.ADMINISTET, False),
            'Administrator':(0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role=Role(name=r)
            role.permissions = roles[r][0]
            role.default=roles[r][1]
            db.session.add(role)
        db.session.commit()


    def __repr__(self):
        return '<Role %r>' %self.name

class Follow(db.Model):
    __tablename__='follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'),primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'),primary_key=True)
    timestamp=db.Column(db.DateTime,default=datetime.utcnow)


class User(UserMixin,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64),unique=True, index=True)
    username = db.Column(db.String(64),unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean,default=False)
    #用户资料信息
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since=db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    questions=db.relationship('Question', backref = 'author', lazy='dynamic')
    answers=db.relationship('Answer',backref='author',lazy='dynamic')
    followed=db.relationship('Follow',foreign_keys=[Follow.follower_id],backref=db.backref('follower',lazy='joined'),
                             lazy='dynamic',cascade='all, delete-orphan')
    followers=db.relationship('Follow',foreign_keys=[Follow.followed_id],backref=db.backref('followed',lazy='joined'),
                              lazy='dynamic',cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default = True).first()


    @property
    def password(self):
        raise AttributeError(u'密码非明文')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    #确认账户 1小时
    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm':self.id})
    def confirm(self,token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data=s.loads(token)
        except:
            return False
        if data.get('confirm')!= self.id:
            return False
        self.confirmed =True
        db.session.add(self)
        return True

    #看用户是否有指定权限
    def can(self, permissions):
        return self.role is not None and (self.role.permissions &permissions)==permissions
    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    #最后登陆时间
    def ping(self):
        self.last_seen=datetime.utcnow()
        db.session.add(self)

    #虚假填充问题
    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py
        seed()
        for i in range(count):
            u=User(email=forgery_py.internet.email_address(),
                   username=forgery_py.internet.user_name(True),
                   password = forgery_py.lorem_ipsum.word(),
                   confirmed=True,
                   name=forgery_py.name.full_name(),
                   location=forgery_py.address.city(),
                   about_me=forgery_py.lorem_ipsum.sentence(),
                   member_since=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()


    def follow(self,user):
        if not self.is_following(user):
            f=Follow(follower=self,followed=user)
            db.session.add(f)

    def unfollow(self,user):
        f=self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self, user):
        return self.followed.filter_by(followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        return self.followers.filter_by(follower_id=user.id).first() is not None

    @property
    def followed_answers(self):
        # return db.session.query(Answer).select_form(Follow).filter_by(follower_id=self.id).join(Answer, Follow.followed_id==Answer.author_id)
        return Answer.query.join(Follow, Follow.followed_id == Answer.author_id)\
            .filter(Follow.follower_id == self.id)

    def __repr__(self):
        return '<User %r>' %self.username

class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False
    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser

@login_manager.user_loader
def load_user(user_id):
    #找到这个用户返回用户对象，没有None
    return User.query.get(int(user_id))


class Question(db.Model):
    __tablename__='questions'
    id=db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html=db.Column(db.Text)
    timestamp = db.Column(db.DateTime,index = True,default=datetime.utcnow)
    author_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    answers=db.relationship('Answer',backref='question',lazy='dynamic')

    #虚假填充问题
    @staticmethod
    def generate_fake(count=100):
        from random import seed,randint
        import forgery_py
        seed()
        user_count=User.query.count()
        for i in range(count):
            u=User.query.offset(randint(0,user_count-1)).first()
            q=Question(body=forgery_py.lorem_ipsum.sentences(randint(1,5)),
                       timestamp=forgery_py.date.date(True),
                       author=u)
            db.session.add(q)
            db.session.commit()

    @staticmethod
    def on_changed_body(target,value,oldvvalue,initiator):
        allowed_tags=['a','abbr','acronyw','b','nlockquote','code','em','i','li','ol','pre','strong','ul','h1','h2','h3','p']
        target.body_html=bleach.linkify(bleach.clean(markdown(value,output_format='html'),
                                                     tags=allowed_tags,strip=True))
db.event.listen(Question.body,'set',Question.on_changed_body)



class Answer(db.Model):
    __tablename__='answers'
    id = db.Column(db.Integer,primary_key=True)
    body=db.Column(db.Text)
    body_html=db.Column(db.Text)
    timestamp=db.Column(db.DateTime,index=True,default=datetime.utcnow)
    disabled=db.Column(db.Boolean)
    author_id=db.Column(db.Integer,db.ForeignKey('users.id'))
    question_id=db.Column(db.Integer,db.ForeignKey('questions.id'))

    @staticmethod
    def on_changed_body(target,value,oldvalue,initiator):
        allowed_tags=['a','abbr','acronym','b','code','em','i','strong']
        target.body_html=bleach.linkify(bleach.clean(markdown(value,output_format='html'),
                                                     tags=allowed_tags,strip=True))

db.event.listen(Answer.body,'set', Answer.on_changed_body)


