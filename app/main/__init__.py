# -*- coding:utf-8 -*-

#蓝本
from flask import Blueprint

main = Blueprint('main',__name__)

from . import views,errors

#示例9-7
from ..models import Permission
@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)