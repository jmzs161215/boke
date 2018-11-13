import datetime
import os

from flask import render_template, request, session, redirect,jsonify
from . import main
from .. import db
from ..models import *

@main.route('/')
def main_index():
    categories = Category.query.all()
    topics = Topic.query.all()
    if 'uid' in session and 'uname' in session:
        user = User.query.filter_by(id=session.get('uid')).first()
    else:
        return redirect('/login')
    return render_template('index.html',params = locals())

@main.route('/login',methods=['GET','POST'])
def login_views():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        loginname = request.form.get('username')
        upwd = request.form.get('password')
        user = User.query.filter_by(loginname=loginname,upwd=upwd).first()

        if user:
            session['uid'] = user.id
            session['uname'] = user.uname
            return redirect('/')
        else:
            errMsg = "用户名或密码不正确"
        return render_template('login.html',errMsg=errMsg)


@main.route('/register',methods=['GET','POST'])
def register_views():
    if request.method == 'GET':
        return render_template('register.html')
    else:

        user = User()
        user.loginname = request.form['loginname']
        user.uname = request.form['username']
        user.email = request.form['email']
        user.url = request.form['url']
        user.upwd = request.form['password']

        db.session.add(user)

        db.session.commit()

        session['uid'] = user.id
        session['uname'] = user.uname
        return redirect('/')


@main.route('/release',methods=['GET','POST'])
def release_views():
  if request.method == 'GET':
    if 'uid' not in session or 'uname' not in session:
      return redirect('/login')
    user = User.query.filter_by(id=session.get('uid')).first()
    categories = Category.query.all()
    blogTypes = BlogType.query.all()
    return render_template('release.html',params=locals())
  else:
    topic = Topic()
    topic.title = request.form.get('author')
    topic.blogtype_id = request.form.get('list')
    topic.category_id = request.form.get('category')
    topic.user_id = session.get('uid')
    topic.content = request.form.get('content')
    topic.pub_date = datetime.datetime.now().strftime("%Y-%m-%d")
    if request.files:
      print('有文件上传')
      f = request.files['picture']
      ftime = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
      ext = f.filename.split('.')[1]
      filename = ftime+"."+ext
      topic.images = 'upload/'+filename
      basedir = os.path.dirname(os.path.dirname(__file__))
      upload_path = os.path.join(basedir,'static/upload',filename)
      print(upload_path)
      f.save(upload_path)
    db.session.add(topic)
    uid = request.form.get('hidden')
    tid = Topic.query.filter_by(title=topic.title).first().id
    user = User.query.get(uid)
    topic = Topic.query.get(tid)
    user.voke_topics.append(topic)
    return redirect('/')

@main.route('/logout')
def logout_views():
    if 'uid' in session and 'uname' in session:
        del session['uid']
        del session['uname']
    return redirect('/')

@main.route('/info',methods=['GET','POST'])
def info_views():
    if request.method == 'GET':
        topic_id = request.args.get('topic_id')
        topic = Topic.query.filter_by(id=topic_id).first()
        topic.read_num = int(topic.read_num) + 1
        db.session.add(topic)
        prevTopic=Topic.query.filter(Topic.id<topic_id).order_by('id desc').first()
        nextTopic=Topic.query.filter(Topic.id>topic_id).first()
    if 'uid' in session and 'uname' in session:
        user = User.query.filter_by(id=session['uid'])
    return render_template('info.html',params=locals())


@main.route('/xiugai',methods=['GET','POST'])
def xiugai_views():
    if request.method == 'GET':
        if 'uid' not in session or 'uname' not in session:
            return redirect('/login')
        user = User.query.filter_by(id=session.get('uid')).first()
        tid = request.args.get('topic_id')
        topic = Topic.query.filter_by(id=tid).first()
        if user.is_author == 1:
            categories = Category.query.all()
            blogTypes = BlogType.query.all()
            return render_template('xiugai.html',params=locals())
        else:
            tid = request.args.get('topic_id')
            topic = Topic.query.filter_by(id=tid).first()
            for x in user.voke_topics.all():
                if int(tid) == x.id:
                    categories = Category.query.all()
                    blogTypes = BlogType.query.all()
                    return render_template('xiugai.html',params=locals())
            return redirect('/')
    else:
        tid = request.form.get('tid')
        topic = Topic.query.filter_by(id=tid).first()
        topic.title = request.form.get('author')
        topic.blogtype_id = request.form.get('list')
        topic.category_id = request.form.get('category')
        topic.user_id = session.get('tid')
        topic.content = request.form.get('content')
        topic.pub_date = datetime.datetime.now().strftime("%Y-%m-%d")
        if request.files:
            print('有文件上传')
            f = request.files['picture']
            ftime = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
            ext = f.filename.split('.')[1]
            filename = ftime + "." + ext
            topic.images = 'upload/' + filename
            basedir = os.path.dirname(os.path.dirname(__file__))
            upload_path = os.path.join(basedir, 'static/upload', filename)
            print(upload_path)
            f.save(upload_path)
        db.session.add(topic)
        return redirect('/')

@main.route('/shanchu')
def shanchu_views():
    uid = request.args.get('user_id')
    tid = request.args.get('topic_id')
    user = User.query.filter_by(id=uid).first()
    topic = Topic.query.filter_by(id=tid).first()
    if user.is_author:
        for user in topic.voke_users.all():
            user.voke_topics.remove(topic)
        db.session.delete(topic)
        return redirect('/')
    else:
        tid = request.args.get('topic_id')
        topic = Topic.query.filter_by(id=tid).first()
        for x in user.voke_topics.all():
            if int(tid) == x.id:
                db.session.delete(topic)
                user.voke_topics.remove(topic)
        return redirect('/')

@main.route('/list')
def list_views():
    cateid = request.args.get('cateid')
    if 'uid' in session and 'uname' in session:
        user = User.query.filter_by(id=session.get('uid')).first()
        if cateid:
            cate = Category.query.filter_by(id=cateid).first()
            topics = cate.topics.all()
            return render_template('list.html', params=locals())
        else:
            categories = Category.query.all()
            topics = Topic.query.all()
            return render_template('list.html', params=locals())
    else:
        return redirect('/login')


@main.route('/time')
def time_views():
    categories = Category.query.all()
    topics = Topic.query.all()
    if 'uid' in session and 'uname' in session:
        user = User.query.filter_by(id=session.get('uid')).first()
    else:
        return redirect('/login')
    return render_template('time.html', params=locals())

@main.route('/gbook')
def gbook_views():
    categories = Category.query.all()
    topics = Topic.query.all()
    replies = Reply.query.all()
    if 'uid' in session and 'uname' in session:
        user = User.query.filter_by(id=session.get('uid')).first()
    else:
        return redirect('/login')
    return render_template('gbook.html', params=locals())

@main.route('/about')
def about_views():
    categories = Category.query.all()
    topics = Topic.query.all()
    if 'uid' in session and 'uname' in session:
        user = User.query.filter_by(id=session.get('uid')).first()
    else:
        return redirect('/login')
    return render_template('about.html', params=locals())