#coding=utf-8
from flask import render_template,redirect,request,url_for,flash,jsonify
from flask_login import login_user,logout_user,login_required,current_user
from . import auth
from .forms import LoginForm,PasswordResetRequestForm,PasswordResetForm
from ..models import User
from .. import db
from ..email import send_email

@auth.route('/login',methods=['GET','POST'])
def login(): 
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user,form.remember_me.data)#在用户会话中把用户标记为已登录，‘记住我’也在表单中填写，如果为True会在用户浏览器中写入一个长期有效的cookie
            return redirect(request.args.get('next') or url_for('main.index'))#Flask-Login会把原地址保存在查询字符串的next参数中
        flash(u'用户名或密码错误')
    return render_template('auth/login.html',form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()#删除并重设用户会话
    flash(u'您已退出登录')
    return redirect(url_for('main.index'))

@auth.route('/register',methods=['GET','POST'])
def register():
    '''
    form=RegistrationForm()
    if form.validate_on_submit():
        user=User(username=form.username.data)
        user.email=form.email.data
        user.password=form.password.data
    '''
    if request.method=="POST":
        user=User(email=request.form.get('email'))
        user.username=request.form.get('username')
        user.password=request.form.get('password')
        db.session.add(user)
        db.session.commit()
        token=user.generate_confirmation_token()
        send_email(user.email,u'确认您的账户','auth/email/confirm',user=user,token=token)
        flash(u'已向您的邮箱发送确认邮件')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')

@auth.route('/registervalidate/email',methods=['POST','GET'])
def registervalidateemail():
    email=request.form.get('email')
    if User.query.filter_by(email=email).first():
        return jsonify(False)
    return jsonify(True)

@auth.route('/registervalidate/username',methods=['POST','GET'])
def registervalidateusername():
    username=request.form.get('username')
    print username
    if User.query.filter_by(username=username).first():
        return jsonify(False)
    return jsonify(True)

@auth.route('/confirm/<token>')
@login_required #Flask-Login提供的login_required修饰器会保护这个路由，用户点击确认邮件中的链接后，要先登录，才能执行这个函数
def confirm(token):
    if current_user.confirmed: #检查是否已经确认过
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash(u'您已经确认过您的账户，谢谢！')
    else:
        flash(u'确认链接无效或已过期')
    return redirect(url_for('main.index'))

#每个程序都可以决定用户确认账户之前可以做哪些操作
@auth.before_app_request #before_request钩子只能应用到属于蓝本的请求上，若想在蓝本中使用针对程序全局请求的钩子，用这个过滤未确认的账户
def before_request():
    #满足以下三点会拦截请求 1.已登录 2.账户还未确认 3.请求的端点不在认证蓝本中
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed and request.endpoint[:5]!='auth.':
            return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

#重新发送确认邮件
@auth.route('/confirmed')
@login_required
def resend_confirmation():
    token=current_user.generate_confirmation_token()
    send_email(current_user.email,u'确认您的账户','auth/email/confirm',user=current_user,token=token)
    flash(u'一封新的确认邮件已经发送到您的邮箱')
    return redirect(url_for('main.index'))

reset_data={}

@auth.route('/reset',methods=['GET','POST'])
def password_reset_request():
    global reset_data
    form=PasswordResetRequestForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user:
            reset_token=user.generate_reset_token()
            reset_data=user.get_reset_token(reset_token)
            send_email(user.email,u'重置密码','auth/email/reset_password',user=user,token=reset_token,next=request.args.get('next'))
            flash(u'已向您的邮箱发送重置密码邮件')
            return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html',form=form)

@auth.route('/reset/<token>',methods=['GET','POST'])
def password_reset(token):
    global reset_data
    print reset_data
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form=PasswordResetForm()
    if form.validate_on_submit():
        user=User.query.filter_by(id=reset_data['reset']).first()
        if user.reset_password(token,form.password.data):
            flash(u'您的密码已经重置')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html',form=form)

