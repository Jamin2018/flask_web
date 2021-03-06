# -*- coding:utf-8 -*-

from flask_mail import Message
from flask import render_template,current_app
from threading import Thread
from . import mail
#集成邮件发送
def send_email(to,subiect,template,**kwargs):
    app = current_app._get_current_object()
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX']+' '+subiect,sender=app.config['FLASKY_MAIL_SENDER'],recipients=[to])
    msg.body = render_template(template+'.txt',**kwargs)
    msg.html = render_template(template+'.html',**kwargs)
    thr = Thread(target=send_async_email,args=[app,msg])
    thr.start()
    return thr

#设置异步发送邮件
def send_async_email(app,msg):
    with app.app_context():
        mail.send(msg)