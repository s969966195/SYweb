#coding=utf-8
from flask import current_app 
from . import db,login_manager
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash #gph(password,method=pbkdf2:sha1,salt_length=8)将原始密码作为输入，以字符串形式输出密码的散列值，输出的值可保存在用户数据库中
                                                                         #cph(hash,password)参数是从数据库中取回的密码散列值和用户输入的密码。返回True表示密码正确
from flask_login import UserMixin #包含Flask-Login要求实现的用户方法is_authenticated is_active is_anonymous get_id()
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer #生成具有过期时间的JSON Web签名，接受的参数是一个密钥，SECRET_KEY设置


class Role(db.Model):
    __tablename__='roles'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(64),unique=True)
    users=db.relationship('User',backref='role')

    def __repr__(self):
        return "<Role '{}'>".format(self.name)

class User(UserMixin,db.Model):
    __tablename__='users'
    id=db.Column(db.Integer(),primary_key=True)
    username=db.Column(db.String(255),unique=True,index=True)
    email=db.Column(db.String(255),unique=True,index=True)
    role_id=db.Column(db.Integer,db.ForeignKey('roles.id'))
    #posts=db.relationship('Post',backref='user',lazy='dynamic')
    password_hash=db.Column(db.String(255))
    confirmed=db.Column(db.Boolean,default=False)

    def __init__(self,username):
        self.username=username

    def __repr__(self): #返回具有可读性的字符串表示模型
        return "<User '{}'>".format(self.username)

    @property #把方法变成属性调用
    def password(self):
        raise AttributeError(u'密码不可读')
    
    @password.setter
    def password(self,password):
        self.password_hash=generate_password_hash(password)

    def verify_password(self,password): #登录时验证密码
        return check_password_hash(self.password_hash,password)

    def generate_confirmation_token(self,expiration=3600): #生成一个令牌，有效期默认为一个小时
        s=Serializer(current_app.config['SECRET_KEY'],expiration) 
        return s.dumps({'confirm':self.id}) #为指定的数据生成一个加密签名，然后再对数据和签名进行序列化

    def confirm(self,token):
        s=Serializer(current_app.config['SECRET_KEY'])
        try:
            data=s.loads(token)
        except:
            return False
        if data.get('confirm')!=self.id: #检查令牌中的id是否和存储在current_user中的已登录用户匹配
            return False
        self.confirmed=True
        db.session.add(self)
        return True
 
@login_manager.user_loader
def load_user(user_id):
    '''加载用户的回调函数'''
    return User.query.get(int(user_id))

'''
tags=db.Table('post_tags',
    db.Column('post_id',db.Integer,db.ForeignKey('posts.id')),
    db.Column('tag_id',db.Integer,db.ForeignKey('tags.id'))
)

class Post(db.Model):
    __tablename__='posts'
    id=db.Column(db.Integer(),primary_key=True)
    text=db.Column(db.Text())
    title=db.Column(db.String(255))
    publish_date=db.Column(db.DateTime(),index=True,default=datetime.utcnow)
    user_id=db.Column(db.Integer(),db.ForeignKey('users.id'))
    comments=db.relationship('Comment',backref='post',lazy='dynamic')
    tags=db.relationship('Tag',secondary=tags,backref=db.backref('posts',lazy='dynamic'))

    def __init__(self,title):
        self.title=title

    def __repr__(self):
        return "<Post '{}'>".format(self.title)

class Comment(db.Model):
    __tablename__='comments'
    id=db.Column(db.Integer(),primary_key=True)
    name=db.Column(db.String(255))
    text=db.Column(db.Text())
    date=db.Column(db.DateTime(),index=True,default=datetime.utcnow)
    post_id=db.Column(db.Integer(),db.ForeignKey('posts.id'))

    def __repr__(self):
        return "<Comment '{}'>".format(self.text[:15])

class Tag(db.Model):
    id=db.Column(db.Integer(),primary_key=True)
    title=db.Column(db.String(255))

    def __init__(self,title):
        self.title=title

    def __repr__(self):
        return "<Tag '{}'>".format(self.title)
'''
