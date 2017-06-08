#coding=utf-8
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField,SubmitField
from wtforms.validators import Required,Length,Email,Regexp,EqualTo
from ..models import User

class LoginForm(FlaskForm): 
    email=StringField('Email',validators=[Required(),Length(1,64),Email()])
    password=PasswordField('PasswordField',validators=[Required()])
    remember_me=BooleanField(u'记住我')
    submit=SubmitField(u'登录')

class RegistrationForm(FlaskForm):
    email=StringField('Email',validators=[Required(),Length(1,46),Email()])
    username=StringField('Username',validators=[Required(),Length(1,46),Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,u'用户名必须只包含字母，数字，下划线和点号')])
    password=PasswordField('Password',validators=[Required(),EqualTo('password2',message=u'两次输入的密码必须一致')])
    password2=PasswordField('Confirm password',validators=[Required()])
    submit=SubmitField(u'注册')

    def validate_email(self,field):
        if User.query.filty_by(email=field.data).first():
            raise ValidationError(u'邮箱已被注册')

    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(u'用户名已被注册')
