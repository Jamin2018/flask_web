# -*- coding:utf-8 -*-

from flask import render_template
from . import auth
from flask import redirect,request,url_for,flash
from flask_login import login_user
from ..models import User
from .forms import LoginForm
from flask_login import logout_user,login_required
from .forms import RegistrationForm
from .. import db
from ..email import send_email
from flask_login import current_user

@auth.route('/login',methods = ['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user,form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password!')
    return render_template('auth/login.html',form = form)

@auth.route('/logout')
@login_required  # 8.4.2保护路由
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index1'))

@auth.route('/register',methods = ['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username = form.username.data,
                    password = form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        # 8.6.2确认邮件的注册路由
        send_email(user.email,'Confirm Your Account',
                   'auth/email/confirm', user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html',form =form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account.Thanks')
    else:
        flash('The confitmation link is invalid or has expired.')
    return redirect(url_for('main.index'))

#钩子   示例8-22  + 示例10-3

@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
                and request.endpoint \
                and request.endpoint[:5] != 'auth.' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))

#示例8-23
@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email,'Confirm Your Account','auth/email/confirm',user = current_user,token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))

@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

