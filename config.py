# coding=utf-8
import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    # Flask-WTF密钥
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sunyuedewangzhan'
    FLASKY_MAIL_SUBJECT_PREFIX = '[SY]'
    FLASKY_MAIL_SENDER = 'SY <s969966195@gmail.com>'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    FLASKY_POSTS_PER_PAGE = 20
    FLASKY_COMMENTS_PER_PAGE = 30
    FLASKY_FOLLOWERS_PER_PAGE = 50
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_RECORD_QUERIES = True  # 启用记录查询统计数字的功能
    FLASKY_SLOW_DB_QUERY_TIME = 0.5  # 缓慢查询的阈值设为0.5
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    BOOTSTRAP_SERVE_LOCAL = True
    UPLOAD_FOLDER = os.getcwd() + '/app/static/avatar/'
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 如果设置成 True (默认情况),
    # Flask-SQLAlchemy 将会追踪对象的修改并且发送信号。这需要额外的内存， 如果不必要的可以禁用它。
    ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']

    @staticmethod
    def init_app(app):
        pass


class ProdConfig(object):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') \
                                or u"mysql://web:web@localhost/r"

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # email errors to the administrators
        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                secure = ()
        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.FLASKY_MAIL_SENDER,
            toaddrs=[cls.FLASKY_ADMIN],
            subject=cls.FLASKY_MAIL_SUBJECT_PREFIX + ' Application Error',
            credentials=credentials,
            secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)


class DevConfig(Config):
    DEBUG = True  # 启用调试
    SQLALCHEMY_DATABASE_URI = u"mysql://web:web@localhost/r"


config = {
    'development': DevConfig,
    'production': ProdConfig,

    'default': DevConfig
}
