#coding:utf-8
#用户认证系统相关的

from flask import Blueprint

auth = Blueprint('auth',__name__)
from . import views