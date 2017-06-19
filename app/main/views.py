#coding:utf-8
from datetime import datetime
from flask import render_template, session, redirect, url_for,current_app,abort,flash,request,make_response
from . import main
from .forms import  EditProfileForm, EditProfileAdminForm,QuestionForm,AnswerForm,SearchForm
from .. import db
from ..models import User,Role,Question,Permission,Answer
from ..email import send_email
from flask_login import login_required,current_user
from ..decorators import admin_required,permission_required


@main.route('/', methods=['GET', 'POST'])
def index():
    form = QuestionForm()
    if current_user.can(Permission.ASK) and form.validate_on_submit():
        question = Question(body=form.body.data,author=current_user._get_current_object())
        db.session.add(question)
        return redirect(url_for('.allquestion'))
    # questions=Question.query.order_by(Question.timestamp.desc()).all()
    #翻页
    page=request.args.get('page',1,type=int)
    # -------------
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_answers
    else:
        query = Answer.query

    pagination = query.order_by(Answer.timestamp.desc()).paginate(page, per_page=current_app.config[
        'FLASKY_ANSWERS_PER_PAGE'],error_out=False)

    # -------------
    # pagination=Question.query.order_by(Question.timestamp.desc()).paginate(page,per_page=current_app.config['FLASKY_QUESTIONS_PER_PAGE'],
    #                                                                        error_out=False)
    answers=pagination.items
    return render_template('index.html',form=form, answers=answers,pagination=pagination,show_followed=show_followed)




#用户资料页
@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    # questions = user.questions.order_by(Question.timestamp.desc()).all()
    # 翻页
    page = request.args.get('page', 1, type=int)
    pagination = user.questions.order_by(Question.timestamp.desc()).paginate(page, per_page=current_app.config[ 'FLASKY_QUESTIONS_PER_PAGE'],
                                                                             error_out=False)
    questions = pagination.items
    answers = user.answers.all()
    return render_template('user.html',user=user, questions=questions,pagination=pagination,answers=answers)

#编辑用户资料
@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        # print chardet.detect(form.about_me.data)
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash(u'个人资料修改成功')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data=current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html',form=form)

#管理员编辑用户资料
@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email=form.email.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location=form.location.data
        user.about_me=form.about_me.data
        db.session.add(user)
        flash(u'用户资料修改成功')
        return redirect(url_for('.user',username=user.username))
    form.email.data=user.email
    form.username.data=user.username
    form.confirmed.data=user.confirmed
    form.role.data = user.role_id
    form.name.data =user.name
    form.location.data=user.location
    form.about_me.data=user.about_me
    return render_template('edit_profile.html',form=form,user=user)

#
@main.route('/question/<int:id>', methods=['GET','POST'])
def question(id):
    question=Question.query.get_or_404(id)
    form = AnswerForm()
    if form.validate_on_submit():
        answer = Answer(body=form.body.data,question=question,author=current_user._get_current_object())
        db.session.add(answer)
        flash(u'回答成功')
        return redirect(url_for('.question',id = question.id,page=-1))
    page = request.args.get('page',1,type=int)
    if page==-1:
        page=(question.answers.count()-1)/current_app.config['FLASKY_ANSWERS_PER_PAGE']+1
    pagination=question.answers.order_by(Answer.timestamp.asc()).paginate(page,per_page=current_app.config['FLASKY_ANSWERS_PER_PAGE'],
                                                                          error_out=False)
    answers = pagination.items
    return render_template('question.html',questions=[question],form=form,answers=answers,pagination=pagination)

@main.route('/edit/<int:id>',methods=['GET','POST'])
@login_required
def edit(id):
    question=Question.query.get_or_404(id)
    if current_user!=question.author and not current_user.can(Permission.ADMINISTER):
        abort(403)
    form =QuestionForm()
    if form.validate_on_submit():
        question.body=form.body.data
        db.session.add(question)
        flash(u'问题修改成功')
        return redirect(url_for('.question',id = question.id))
    form.body.data=question.body
    return render_template('edit_question.html', form=form)

@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_ANSWER)
def moderate():
    page = request.args.get('page',1,type=int)
    pagination=Answer.query.order_by(Answer.timestamp.desc()).paginate(page,per_page=current_app.config['FLASKY_ANSWERS_PER_PAGE'],error_out=False)
    answers=pagination.items
    return render_template('moderate.html',answers=answers,pagination=pagination,page=page)



@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_ANSWER)
def moderate_enable(id):
    comment = Answer.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))


@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_ANSWER)
def moderate_disable(id):
    comment = Answer.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))


@main.route('/search',methods=['GET','POST'])
def search_page():
    form = SearchForm()
    if form.validate_on_submit():
        searchs=Question.query.filter(Question.body.ilike('%'+form.body.data+'%')).all()
        if len(searchs)!=0:
            # questions=Question.query.order_by(Question.timestamp.desc()).all()
            # 翻页
            page = request.args.get('page', 1, type=int)
            pagination = Question.query.filter(Question.body.ilike('%'+form.body.data+'%')).order_by(Question.timestamp.desc()).paginate(page, per_page=current_app.config[
            'FLASKY_QUESTIONS_PER_PAGE'],
                                                                                 error_out=False)
            searches = pagination.items
            # print len(searchs)
            # print searchs
            # print form.body.data
            # print 'sss',searches
            flash(u'搜到相关问题如下，没有满意的可以去首页提问哦！')
            return render_template('search.html',questions=searches,pagination=pagination,form=form)
        flash(u'没有搜到相应问题，你可以去主页提问哦！')
        return redirect(url_for('.search_page'))
    return render_template('search.html',form=form)

@main.route('/questionlist',methods=['GET','POST'])
def allquestion():
    questions = Question.query.order_by(Question.timestamp.desc()).all()
    page = request.args.get('page', 1, type=int)
    pagination = Question.query.order_by(Question.timestamp.desc()).paginate(page, per_page=current_app.config[
        'FLASKY_QUESTIONS_PER_PAGE'],
                                                                             error_out=False)
    questions = pagination.items
    return render_template('questionlist.html',questions=questions, pagination=pagination)


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'没有这个用户.')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash(u'你已经关注过该用户了')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    flash(u'成功关注 %s.' % username)
    return redirect(url_for('.user', username=username))

@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'没有这个用户.')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash(u'你已经关注过该用户了')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    flash(u'你已经不再关注 %s 了.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'没有这个用户.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followers of",
                           endpoint='.followers', pagination=pagination,
                           follows=follows)


@main.route('/followed-by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'没有这个用户.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followed by",
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)

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