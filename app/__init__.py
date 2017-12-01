# -*- coding:utf-8 -*-

from flask import Flask,render_template
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_login import LoginManager
from flask_pagedown import PageDown   #11.4.1 富文本文章

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
pagedown = PageDown()
#用户认证
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'



def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])  #这个不懂
    config[config_name].init_app(app)

    bootstrap.init_app(app)   # --> bootstrap = Bootstrap(app)
    mail.init_app(app)       # --> mail = Mail(app)
    moment.init_app(app)   # --> moment = Moment(app)
    db.init_app(app)    # --> db = SQLAlchemy(app)

    login_manager.init_app(app)
    pagedown.init_app(app)
    #注册路由蓝本
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    #注册登录蓝本
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint,url_prefix = '/auth')  #url_prefix是给路由添加指定前缀，可选参数
    #附加路由和自定义的错误页面

    return app

