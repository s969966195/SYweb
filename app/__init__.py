# -*- coding:utf-8 -*-
from flask import Flask
from config import config
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_mail import Mail
from flask_login import LoginManager
from flask_pagedown import PageDown

bootstrap=Bootstrap()
db=SQLAlchemy()
moment=Moment()
mail=Mail()
pagedown=PageDown()

login_manager=LoginManager()
login_manager.session_protection='strong'#提供不同的安全等级防止用户会话遭篡改,'strong'会记录客户端IP地址和浏览器的用户代理信息,如果发现异动就登出用户 None,'basic'
login_manager.login_view='auth.login'

def create_app(config_name):
    app=Flask(__name__)
    app.config.from_object(config[config_name]) #加载配置
    config[config_name].init_app(app)
    
    db.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint,url_prefix='/auth')

    return app
