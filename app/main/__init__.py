#coding:utf-8
#蓝本
from flask import Blueprint
main = Blueprint('main', __name__)
#路由在views，错误是在errors
from . import views,errors
from ..models import Permission
#把permission加入上下文
@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)