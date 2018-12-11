import os
import smtplib
from email.mime.text import MIMEText
import secrets
import csv
import datetime
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort, session
from flask_login import login_user, current_user, logout_user, login_required,LoginManager,UserMixin
from flask_mail import Message
from flaskblog import app, db, bcrypt, mail, login_manager
from flaskblog.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                             PostForm, RequestResetForm, ResetPasswordForm)
from flaskblog.models import User
from flaskblog.oauth import OAuthSignIn
from flaskblog.DataAnalysis import analyse, extractData, show_output
from flaskblog.DataVisualization import sentimentAnalysis, graphOutput, geolocation
from flaskblog.FileLocations import file_locations

from flask_sqlalchemy import SQLAlchemy

PEOPLE_FOLDER = os.path.join('static', 'graph')

app.config['UPLOAD_FOLDER'] = PEOPLE_FOLDER


app.config['OAUTH_CREDENTIALS'] = {
    'facebook': {
        'id': '2153453314930869',
        'secret': '10e584ebb56b4f8fa1f2fa133768418f'
    },
    'twitter': {
        'id': 'uajXzMsBMi55XdCkoCWoyFbmC',
        'secret': 'oEcTTZblSA8Mewn5Lx9wSQFLzr0J7m57V4SMRDzPvSYrUBBlv7'
    },

    'google': {
        'id': '426804271451-6gtjb3gcnndpqvp69i67quikh7ht1crq.apps.googleusercontent.com',
        'secret': 'tZ0n7JGY0CnewUwEcpJtX6d2'
    }
}

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('login'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('login'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email = oauth.callback()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('login'))
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        user = User(social_id=social_id, username=username, email=email)
        db.session.add(user)
        db.session.commit()
    login_user(user, True)
    return redirect(url_for('dashboard'))


@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    return render_template('landing.html')


@app.route("/contactus")
def contactus():

    return render_template('contactus.html')


@app.route("/map")
@login_required
def map():
    return render_template('map.html')


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template("index.html")


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/analysis')
@login_required
def analysis():
    return render_template("analysis.html")


@app.route('/contactusresponse',methods = ['POST', 'GET'])
@login_required
def contactusresponse():
    email= request.form['Email']
    message = request.form['Message']
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login("twitterapptry@gmail.com", "twitter123")
    msg = MIMEText(message)
    msg['Subject'] = "Query: " + email
    s.sendmail(current_user.email, "twitterapptry@gmail.com", msg.as_string())
    s.quit()
    flash("Your Message has Been send successfully")
    return render_template('contactus.html')


@app.route('/analysisresult',methods = ['POST', 'GET'])
@login_required
def analysisresult():
    extract_data = extractData.ExtractData()
    analyse_data = analyse.Analyse()
    # inputs = input_key_date.TakeInput()
    hashtag = request.form['hashtag']
    startdate = request.form['startdate']
    enddate = request.form['enddate']

    if str(hashtag).lower() == "lotus":
        hashtag_lotus, hashtag_karaoke = True, False
        location = file_locations.lotus_withoutDate
    elif str(hashtag).lower() == "karaoke":
        hashtag_karaoke, hashtag_lotus = True, False
        location = file_locations.karaoke_withoutDate
    else:
        hashtag_lotus, hashtag_karaoke = False, False
        location = file_locations.dataset

    if startdate == "" and enddate == "":
        to_date = datetime.datetime.now()
        from_date = "1"
    else:
        to_date = datetime.datetime(int(enddate.split("-")[0]),
                                   int(enddate.split("-")[1]), int(enddate.split("-")[2]), 23, 59, 59)
        from_date = "1"

    if hashtag_lotus==False and hashtag_karaoke==False:
        csvFile = open(file_locations.dataset, 'w')
        csvWriter = csv.writer(csvFile)
        analyse_data.analysis(extract_data.authorize(), hashtag, from_date, to_date, csvWriter)

    df = pd.read_csv(location, names=['created_at', 'tweets', 'username', 'likes', 'retweet', 'coordinates'])

    show_data = show_output.ShowOutput()
    total, people = show_data.print_output(df)
    user_name = people['username'].str.extract(r'\'(.*)\'').values
    user_name = [item for sublist in user_name for item in sublist]
    tweets = people['tweets']

    # ----------sentiment analysis graph
    senti = sentimentAnalysis.SentimentAnalysis()
    polarity = senti.polarity_analysis(df)
    senti.show_graph()
    tenHashTagsPolarity = senti.ten_hashtags_polarity(df)
    FirstTenTweets = tenHashTagsPolarity['Tweets']
    sentiment = tenHashTagsPolarity['Sentiment']
    # ----------sentiment analysis graph

    # ----------graph output
    graph = graphOutput.GenerateGraph()
    d = df.groupby(df["created_at"].str[0:10])
    graph.num_hashtags(d, plt)
    graph.num_likes_retweets(d, plt)
    graph.top_hashtags(df, plt)
    # ----------graph output

    # ----------geolocation output
    geo = geolocation.Geo()
    geo.plot_gmap(df)
    # ----------geolocation output

    full_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'sentigraph.png')
    numofhashtags = os.path.join(app.config['UPLOAD_FOLDER'], 'numofhashtags.png')
    numoflikes = os.path.join(app.config['UPLOAD_FOLDER'], 'numoflikes.png')
    toptenusers = os.path.join(app.config['UPLOAD_FOLDER'], 'toptenusers.png')
    templs = ["analysis.html", "sentimentanalysis.html"]
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template(templs, total=total, people=people, user_name=user_name, tweets=tweets, graph=full_filename,
                           graph2=toptenusers, graph3=numoflikes, graph4=numofhashtags, flag=1, image_file=image_file,
                           polarity=polarity, sentiment=sentiment, FirstTenTweets=FirstTenTweets)


@app.route('/analysisresultwithdate', methods=['POST', 'GET'])
@login_required
def analysisresultwithdate():
    extract_data = extractData.ExtractData()
    analyse_data = analyse.Analyse()
    # inputs = input_key_date.TakeInput()
    hashtag = request.form['hashtag']
    startdate = request.form['startdate']
    enddate = request.form['enddate']
    if str(hashtag).lower() == "lotus":
        hashtag_lotus, hashtag_karaoke = True, False
        location = file_locations.lotus_fourToEight
        location_withoutDate = file_locations.lotus_withoutDate
    elif str(hashtag).lower() == "karaoke":
        hashtag_karaoke, hashtag_lotus = True, False
        location = file_locations.karaoke_sixToEight
        location_withoutDate = file_locations.karaoke_withoutDate
    else:
        hashtag_lotus, hashtag_karaoke = False, False
        location = file_locations.dataset
        location_withoutDate = file_locations.dataset

    if startdate == "" and enddate == "":
        to_date = datetime.datetime.now()
        from_date = "1"
    else:
        to_date = datetime.datetime(int(enddate.split("-")[0]),
                                   int(enddate.split("-")[1]), int(enddate.split("-")[2]), 23, 59, 59)
        from_date = startdate

    if hashtag_lotus == False and hashtag_karaoke == False:
        csvFile = open(file_locations.dataset, 'w')
        csvWriter = csv.writer(csvFile)
        analyse_data.analysis(extract_data.authorize(), hashtag, from_date, to_date, csvWriter)

    df = pd.read_csv(location, names=['created_at', 'tweets', 'username', 'likes', 'retweet', 'coordinates'])
    df_withoutDate = pd.read_csv(location_withoutDate, names=['created_at', 'tweets', 'username',
                                                              'likes', 'retweet', 'coordinates'])

    show_data = show_output.ShowOutput()
    total, people = show_data.print_output(df)
    user_name = people['username'].str.extract(r'\'(.*)\'').values
    user_name = [item for sublist in user_name for item in sublist]
    tweets = people['tweets']

    # ----------sentiment analysis graph
    senti = sentimentAnalysis.SentimentAnalysis()
    polarity = senti.polarity_analysis(df)
    senti.show_graph()
    tenHashTagsPolarity = senti.ten_hashtags_polarity(df)
    FirstTenTweets = tenHashTagsPolarity['Tweets']
    sentiment = tenHashTagsPolarity['Sentiment']
    # ----------sentiment analysis graph

    # ----------graph output
    graph = graphOutput.GenerateGraph()
    d = df.groupby(df["created_at"].str[0:10])
    graph.num_hashtags(d, plt)
    graph.num_likes_retweets(d, plt)
    graph.top_hashtags(df, plt)
    # ----------graph output

    # ----------geolocation output
    geo = geolocation.Geo()
    geo.plot_gmap(df_withoutDate)
    # ----------geolocation output

    full_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'sentigraph.png')
    numofhashtags = os.path.join(app.config['UPLOAD_FOLDER'], 'numofhashtags.png')
    numoflikes = os.path.join(app.config['UPLOAD_FOLDER'], 'numoflikes.png')
    toptenusers = os.path.join(app.config['UPLOAD_FOLDER'], 'toptenusers.png')
    templs = ["analysis.html", "sentimentanalysis.html"]
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template(templs, total=total, people=people, user_name=user_name, tweets=tweets, graph=full_filename,
                           graph2=toptenusers, graph3=numoflikes, graph4=numofhashtags, flag=1, image_file=image_file,
                           polarity=polarity, sentiment=sentiment, FirstTenTweets=FirstTenTweets)





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
    return render_template('profile.html', title='Account',
                           image_file=image_file, form=form)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    # return render_template('reset_request.html', title='Reset Password', form=form)
    return render_template('forgotpassword.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('forgotpasswordtoken.html', title='Reset Password', form=form)
