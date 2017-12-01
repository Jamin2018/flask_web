# -*- coding:utf-8 -*-

from flask import Flask
from flask_script import Manager   #扩展命令
from flask import render_template      #模板管理 --> 表现代码（html）
from flask_bootstrap import Bootstrap    #使用Bootstrap基模板
from flask import url_for
from flask_moment import Moment    #格式化时间
from datetime import datetime
from flask_wtf import Form    #简单的表单
from wtforms import StringField,SubmitField
from wtforms.validators import Required

from flask import session,redirect
from flask import flash
from flask_sqlalchemy import SQLAlchemy
import os
from flask_script import Shell
from flask_migrate import Migrate,MigrateCommand
from flask_mail import Mail
from flask_mail import Message
from threading import Thread

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)

app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
#设置邮箱
app.config['MAIL_SERVER'] = 'smtp.qq.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')   #set MAIL_USERNAME=389098898 ,set环境变量不是永久性的，所以每次都要重新set
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')   #set MAIL_PASSWORD=epwstgslysabbhid / cdhsdjkcutenbhgh
#添加集成发送邮件功能
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['FLASKY_MAIL_SENDER']='389098898@qq.com'
app.config['FLASKY_ADMIN']=os.environ.get('FLASKY_ADMIN')  #谁接收邮件    set FLASKY_ADMIN=389098898@qq.com

manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
mail = Mail(app)

@app.route('/',methods=['GET','POST'])

def index():
    # name = None
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.name.data).first()
        # old_name = session.get('name')
        if user is None:
            user = User(username = form.name.data)
            db.session.add(user)
            session['known'] = False
            print '111'
            print app.config['MAIL_USERNAME']
            print app.config['FLASKY_ADMIN']
            if app.config['FLASKY_ADMIN']:
                send_email(app.config['FLASKY_ADMIN'],'New User','mail/new_user',user = user)
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        # if old_name is not None and old_name != form.name.data:
        #     flash(('你改变了名字!').decode('utf8'))
        return redirect(url_for('index'))
    return render_template('index.html',form = form,name=session.get('name'),
                           known = session.get('known',False),current_time = datetime.utcnow())

@app.route('/user/<name>')   #注意要用<>括起来
def user(name):
    return render_template('user.html',name = name)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'),500


# 表单验证
class NameForm(Form):
    name = StringField('What is your name?',validators=[Required()])
    submit = SubmitField('Submit')


#数据库模型
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64),unique= True)
    users = db.relationship('User',backref = 'role',lazy = 'dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(64),unique=True,index = True)
    role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username

#集成邮件发送
def send_email(to,subiect,template,**kwargs):
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




#回调函数，让shell命令自动导入特定的对象
def make_shell_context():
    return dict(app=app,db=db,User=User,Role=Role)
manager.add_command('shell',Shell(make_context=make_shell_context))

#创建迁移仓库
migrate = Migrate(app,db)
manager.add_command('db',MigrateCommand)


if __name__ == '__main__':
    # manager.run()
    app.run(debug=True)