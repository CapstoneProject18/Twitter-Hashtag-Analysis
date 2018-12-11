from flaskblog import app, models


if __name__ == '__main__':
    models.db.create_all()
    app.run(debug=True,ssl_context='adhoc')
