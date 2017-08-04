#coding=utf-8
import os
basedir=os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY=os.environ.get('SECRET_KEY') or 'hard to guess string'#Flask-WTF密钥
    FLASKY_MAIL_SUBJECT_PREFIX='[SY]'
    FLASKY_MAIL_SENDER='SY <s969966195@gmail.com>'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    FLASKY_POSTS_PER_PAGE = 20
    FLASKY_COMMENTS_PER_PAGE=30
    FLASKY_FOLLOWERS_PER_PAGE=50

    @staticmethod 
    def init_app(app):
        pass

class ProdConfig(object):
    pass

class DevConfig(Config): 
    DEBUG=True #启用调试
    SQLALCHEMY_DATABASE_URI=u"mysql://web:web@localhost/r"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER='smtp.gmail.com'
    MAIL_PORT=587
    MAIL_USE_TLS=True
    MAIL_USE_SSL=False
    MAIL_USERNAME=os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD')
    BOOTSTRAP_SERVE_LOCAL = True
    UPLOAD_FOLDER=os.getcwd()+'/app/static/avatar/'
    SQLALCHEMY_TRACK_MODIFICATIONS=False #如果设置成 True (默认情况)，Flask-SQLAlchemy 将会追踪对象的修改并且发送信号。这需要额外的内存， 如果不必要的可以禁用它。
    ALLOWED_EXTENSIONS=['png','jpg','jpeg','gif']

config={
    'development':DevConfig,
    'production':ProdConfig,
    
    'default':DevConfig
}
