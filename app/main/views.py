#coding=utf-8
from datetime  import datetime
from flask import render_template,session,redirect,url_for,flash,current_app

from . import main
from .forms import NameForm
from .. import db
from ..models import User
from ..email import send_email

def quote_buffer(buf):
    '''mysql处理中文'''
    retstr=''.join(map(lambda c:'%02x'%ord(c),buf))
    retstr="x'"+retstr+"'"
    return retstr

@main.route('/',methods=['GET','POST'])
def index():
    form=NameForm()
    if form.validate_on_submit():
        username=quote_buffer(form.name.data)
        user=User.query.filter_by(username=username).first()
        if user is None:
            user=User(username=form.name.data)
            db.session.add(user)
            session['known']=False
            if current_app.config['FLASKY_ADMIN']:
                send_email(current_app.config['FLASKY_ADMIN'],u'新用户','email/new_user',user=user)
        else:
            session['known']=True
        session['name']=form.name.data
        form.name.data=''
        return redirect(url_for('.index'))
    return render_template('index.html',form=form,name=session.get('name'),known=session.get('known',False),current_time=datetime.utcnow())
    
