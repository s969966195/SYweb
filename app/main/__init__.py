# coding=utf-8
'''main蓝图'''
from flask import Blueprint
from ..models import Permission

main = Blueprint('main', __name__)

from . import views, errors


@main.app_context_processor  # 上下文处理器能让变量在所有模板中全局可访问
def inject_permissions():
    return dict(Permission=Permission)
