import os
import secrets
from PIL import Image       #pip install pillow
from flask import render_template, url_for, flash, redirect, request, abort
from flask1 import app, db, bcrypt
from flask1.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, SearchForm
from flask1.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required

@app.route("/")
@app.route("/home")
def home():
    return render_template('about.html')


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('all_posts'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('all_posts'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            # return redirect(url_for('home'))
            flash('You have been logged in!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('all_posts'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(patient= form.patient.data, diagnosis = form.diagnosis.data, content=form.content.data, doctor=current_user)
        db.session.add(post)
        db.session.commit()
        flash('your diagnosis is complete!', 'success')
        return redirect(url_for('all_posts'))
    return render_template('create_post.html', title='New post', 
                            form=form, legend = 'New Post')

@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.patient, post=post)

@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if(post.doctor != current_user):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.patient = form.patient.data
        post.diagnosis = form.diagnosis.data
        post.content = form.content.data
        db.session.commit()
        flash('Your diagnosis has been updated!', 'success')
        return redirect(url_for('post',post_id=post.id))
    elif request.method == 'GET':
        form.patient.data = post.patient
        form.diagnosis.data = post.diagnosis
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post', 
                            form = form, legend = 'Update Post')

@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if(post.doctor != current_user):
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!','success')
    return redirect(url_for('all_posts'))

@app.route("/home/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(doctor=user)\
            .order_by(Post.date_posted.desc())\
            .paginate(page=page, per_page=5)
    return render_template('user_post.html', posts=posts, user=user)

@app.route("/all")
def all_posts():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('all_posts.html', posts=posts)

@app.route("/search", methods=['GET', 'POST'])
def search():
    form = SearchForm()
    p=form.patient.data
    if request.method=='POST':
        return search_posts(p)
    return render_template('search.html',form=form)

@app.route("/search_results/")
def search_posts(patient):
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(patient=patient)\
            .order_by(Post.date_posted.desc())\
            .paginate(page=page, per_page=5)
    return render_template('search_posts.html', posts=posts)