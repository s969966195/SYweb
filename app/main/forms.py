#coding=utf-8
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,TextField
from wtforms.validators import Required,Length
from flask_pagedown.fields import PageDownField

class NameForm(FlaskForm):
    name=StringField(u'你的名字？',validators=[Required()])
    submit=SubmitField(u'提交')

class EditProfileForm(FlaskForm):
    username=StringField(u'昵称',validators=[Length(0,64)])
    location=StringField(u'地点',validators=[Length(0,64)])
    about_me=TextField(u'个人简介')
    submit=SubmitField(u'提交')

class PostForm(FlaskForm):
    title=StringField(u'标题',validators=[Required(),Length(0,64)])
    text=PageDownField(u'正文',validators=[Required()])
    submit=SubmitField(u'提交')

class CommentForm(FlaskForm):
    body=StringField('',validators=[Required()])
    submit=SubmitField(u'提交')
