# coding=utf-8
from datetime import datetime
from flask import render_template, redirect, url_for, flash, current_app, request, make_response, abort
from flask_login import login_required, current_user
from . import main
from .forms import EditProfileForm, PostForm, CommentForm
from .. import db
from ..models import User, Permission, Post, Comment
from ..decorators import permission_required


def quote_buffer(buf):
    '''mysql处理中文'''
    retstr = ''.join(map(lambda c: '%02x' % ord(c), buf))
    retstr = "x'" + retstr + "'"
    return retstr


@main.route('/', methods=['GET', 'POST'])
def index():
    '''
    username=quote_buffer(form.name.data)
    user=User.query.filter_by(username=username).first()
    '''
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post(title=form.title.data, text=form.text.data, author=current_user._get_current_object())  # 数据库需要真正的用户对象,所以调用_get_current_object()对象
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.index'))
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))  # 在show_all和show_followed两个路由中决定
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(Post.publish_date.desc()).paginate(page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)  # 按时间戳降序排列
    posts = pagination.items
    return render_template('index.html', pagination=pagination, form=form, posts=posts, show_followed=show_followed, current_time=datetime.utcnow())


@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
    return resp


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.publish_date.desc()).paginate(page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)  # 按时间戳降序排列
    posts = pagination.items
    return render_template('user.html', user=user, posts=posts)


@main.route('/change-avatar', methods=['GET', 'POST'])
@login_required
def change_avatar():
    if request.method == "POST":
        avatar = request.files['avatar']
        fname = avatar.filename
        UPLOAD_FOLDER = current_app.config['UPLOAD_FOLDER']
        ALLOWED_EXTENSIONS = current_app.config['ALLOWED_EXTENSIONS']
        flag = '.' in fname and fname.split('.')[1] in ALLOWED_EXTENSIONS
        if not flag:
            flash(u'不支持该类型文件')
            return redirect(url_for('.user', username=current_user.username))
        avatar.save('{}{}_{}'.format(UPLOAD_FOLDER, str(current_user.username), str(fname)))
        current_user.real_avatar = '/static/avatar/{}_{}'.format(current_user.username, fname)
        db.session.add(current_user)
        db.session.commit()
        return redirect(url_for('.user', username=current_user.username))


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        if current_user.username != form.username.data and User.query.filter_by(username=form.username.data).first():
            flash(u'昵称已被占用')
            return redirect(url_for('.edit_profile'))
        current_user.username = form.username.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        db.session.commit()
        flash(u'您的个人信息已更新')
        return redirect(url_for('.user', username=current_user.username))
    form.username.data = current_user.username
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)  # 插入数据库时的id
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data, post=post, author=current_user._get_current_object())
        db.session.add(comment)
        db.session.commit()
        flash(u'评论成功')
        return redirect(url_for('.post', id=post.id, page=-1))  # 请求评论的最后一页
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count()-1) / current_app.config['FLASKY_COMMENTS_PER_PAGE']+1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'], error_out=False)
    comments = pagination.items
    return render_template('post.html', posts=[post], form=form, comments=comments, pagination=pagination)


@main.route('/like/<int:id>', methods=['GET', 'POST'])
def like(id):
    post = Post.query.get_or_404(id)
    user = current_user._get_current_object()
    post.like.append(user)
    db.session.add(post)
    db.session.commit()
    return 'OK'


@main.route('/edit-post/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.text = form.text.data
        db.session.add(post)
        db.session.commit()
        flash(u'文章已经更新')
        return redirect(url_for('.post', id=post.id))
    form.title.data = post.title
    form.text.data = post.text
    return render_template('edit_post.html', form=form, post=post)


@main.route('/edit-post', methods=['GET', 'POST'])
@login_required
def edit_post_new():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post(title=form.title.data, text=form.text.data, author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        flash(u'发表文章成功')
        return redirect(url_for('.index'))
    return render_template('edit_post.html', form=form)


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'无效的用户')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash(u'您已经关注过此用户')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    flash(u'您现在已关注%s' % username)
    return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'无效的用户')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash(u'您还没有关注过此用户')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    flash(u'已经取消关注%s' % username)
    return redirect(url_for('.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'用户不存在')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'], error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp} for item in pagination.items]
    return render_template('followers.html', user=user, title=u"关注列表", endpoint='.followers', pagination=pagination, follows=follows)


@main.route('/followed-by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'用户不存在')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'], error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp} for item in pagination.items]
    return render_template('followers.html', user=user, title=u"关注列表", endpoint='.followed_by', pagination=pagination, follows=follows)


@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'], error_out=False)
    comments = pagination.items
    return render_template('moderate.html', comments=comments, pagination=pagination, page=page)


@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.moderate', page=request.args.get('page', 1, type=int)))


@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.moderate', page=request.args.get('page', 1, type=int)))
