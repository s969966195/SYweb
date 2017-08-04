#coding=utf-8
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,TextField,TextAreaField
from wtforms.validators import Required,Length
from flask_pagedown.fields import PageDownField

class NameForm(FlaskForm):
    name=StringField(u'你的名字？',validators=[Required()])
    submit=SubmitField(u'提交')

class EditProfileForm(FlaskForm):
    username=StringField(u'昵称',validators=[Length(0,64)])
    location=StringField(u'地点',validators=[Length(0,64)])
    about_me=PageDownField(u'个人简介')
    submit=SubmitField(u'提交')

class PostForm(FlaskForm):
    title=StringField(u'标题',validators=[Required(message=u"请输入标题"),Length(0,64)])
    text=TextAreaField(u'正文',validators=[Required(message=u"请输入文章内容")])
    submit=SubmitField(u'提交')

class CommentForm(FlaskForm):
    body=StringField('',validators=[Required()])
    submit=SubmitField(u'提交')
