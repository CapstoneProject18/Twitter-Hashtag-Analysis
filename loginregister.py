from flask import Flask, render_template, request, redirect, url_for, session
from flask_oauth import OAuth
import askForConnections
import analyse
import extractData
import input_key_date
import csv
import tweepy
import show_output
import datetime

# Google Configs
GOOGLE_CLIENT_ID = '665465619766-u41sjqdbdehlucnl8srhhmar7d9d9fm6.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = '_j3fi51pAM-E_258I42Gzvji'
REDIRECT_URI = '/oauth2callback'  # one of the Redirect URIs from Google APIs console

SECRET_KEY = 'development key'
DEBUG = True

app = Flask(__name__)
app.debug = DEBUG
app.secret_key = SECRET_KEY
oauth = OAuth()

google = oauth.remote_app('google',
                          base_url='https://www.google.com/accounts/',
                          authorize_url='https://accounts.google.com/o/oauth2/auth',
                          request_token_url=None,
                          request_token_params={'scope': 'https://www.googleapis.com/auth/userinfo.email',
                                                'response_type': 'code'},
                          access_token_url='https://accounts.google.com/o/oauth2/token',
                          access_token_method='POST',
                          access_token_params={'grant_type': 'authorization_code'},
                          consumer_key=GOOGLE_CLIENT_ID,
                          consumer_secret=GOOGLE_CLIENT_SECRET)


@app.route('/')
@app.route('/login.html', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        print('inside Post')
        if request.form.get('Login') == 'Login':
            userDetails = request.form
            username = userDetails['Username']
            password = userDetails['Password']
            try:
                # Ask for connection
                connection = askForConnections.getConnection()
                print("Connection successful!")
                cursor = connection.cursor()
                cursor.execute("SELECT Email, Password from register where Email='" + email + "' and Password='" + password + "'")
                data = cursor.fetchone()
                if data is None:
                    return "Wrong Credentials"
                else:
                    return redirect(url_for('dashboard'))
            finally:
                connection.close()
        print('Before google login')
        if request.form.get('GoogleLogin') == 'GoogleLogin':
            print('Inside Elif')
            access_token = session.get('access_token')
            if access_token is None:
                return redirect(url_for('glogin'))

            access_token = access_token[0]
            from urllib.request import Request, urlopen
            from urllib.error import URLError

            headers = {'Authorization': 'OAuth ' + access_token}
            req = Request('https://www.googleapis.com/oauth2/v1/userinfo',
                          None, headers)
            try:
                res = urlopen(req)
            except URLError as e:
                if e.code == 401:
                    # Unauthorized - bad token
                    session.pop('access_token', None)
                    return redirect(url_for('glogin'))
                return res.read()
            return res.read()

    return render_template('login.html')


@app.route('/register.html', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Fetching data from the form
        userDetails = request.form
        name = userDetails['name']
        email = userDetails['email']
        password = userDetails['password']

        try:
            connection = askForConnections.getConnection()
            print("Connection successful!")
            cursor = connection.cursor()

            sql = "Insert into register (Name, Email, Password) " \
                  + " values (%s, %s, %s) "

            # Execute sql, and pass two parameters.
            cursor.execute(sql, (name, email, password))

            connection.commit()
            print("Data Insertion Successful")
            return redirect(url_for('login'))
        finally:
            connection.close()
    return render_template("register.html")


@app.route('/dashboard')
def dashboard():
    return render_template("index.html")


@app.route('/glogin')
def glogin():
    callback = url_for('authorized', _external=True)
    return google.authorize(callback=callback)


@app.route(REDIRECT_URI)
@google.authorized_handler
def authorized(resp):
    access_token = resp['access_token']
    session['access_token'] = access_token, ''
    return redirect(url_for('dashboard'))


@google.tokengetter
def get_access_token():
    return session.get('access_token')


@app.route('/analysis')
def analysis():
    return render_template("analysis.html")


@app.route('/analysisresult',methods = ['POST', 'GET'])
def analysisresult():
    extract_data = extractData.ExtractData()
    analyse_data = analyse.Analyse()
    # inputs = input_key_date.TakeInput()
    hashtag = request.form['hashtag']
    startdate = request.form['startdate']
    enddate = request.form['enddate']

    if startdate == "" and enddate == "":
        to_date = datetime.datetime.now()
        from_date = "1"
    else:
        to_date = datetime.datetime(int(enddate.split("-")[0]),
                                   int(enddate.split("-")[1]), int(enddate.split("-")[2]), 23, 59, 59)
        from_date = "1"

    csvFile = open('data.csv', 'w')
    csvWriter = csv.writer(csvFile)
    analyse_data.analysis(extract_data.authorize(), hashtag, from_date, to_date, csvWriter)

    show_data = show_output.ShowOutput()
    total, people = show_data.print_output()

    return render_template("analysis.html",total=total, people=people)


@app.route('/analysisresultwithdate',methods = ['POST', 'GET'])
def analysisresultwithdate():
    extract_data = extractData.ExtractData()
    analyse_data = analyse.Analyse()
    # inputs = input_key_date.TakeInput()
    hashtag = request.form['hashtag']
    startdate = request.form['startdate']
    enddate = request.form['enddate']

    if startdate == "" and enddate == "":
        to_date = datetime.datetime.now()
        from_date = "1"
    else:
        to_date = datetime.datetime(int(enddate.split("-")[0]),
                                   int(enddate.split("-")[1]), int(enddate.split("-")[2]), 23, 59, 59)
        from_date = "1"

    csvFile = open('data.csv', 'w')
    csvWriter = csv.writer(csvFile)
    analyse_data.analysis(extract_data.authorize(), hashtag, from_date, to_date, csvWriter)

    show_data = show_output.ShowOutput()
    total, people = show_data.print_output()

    return render_template("analysis.html",total = total, people = people)


@app.route('/contactus')
def contactus():
    return render_template("contactus.html")


if __name__ == '__main__':
    app.run(debug="True")
