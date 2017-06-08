#coding=utf-8
from flask import render_template,redirect,request,url_for,flash
from flask_login import login_user,logout_user,login_required
from . import auth
from .forms import LoginForm
from ..models import User


@auth.route('/login',methods=['GET','POST'])
def login(): 
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filty_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user,form.remember_me.data)#在用户会话中把用户标记为已登录，‘记住我’也在表单中填写，如果为True会在用户浏览器中写入一个长期有效的cookie
            return redirect(request.args.get('next') or url_for('main.index'))#Flask-Login会把原地址保存在查询字符串的next参数中
        flash(u'用户名或密码错误')
    return render_template('login.html',form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()#删除并重设用户会话
    flash(u'您已退出登录')
    return redirect(url_for('main.index'))

