#!/usr/bin/env python
#coding=utf-8
import MySQLdb
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, abort,\
        render_template, flash

# configuration
DATABASE_HOST = 'localhost'
DATABASE_USERNAME= 'root' 
DATABASE_PASSWORD = 'root'
DATABASE_DB = 'silegon'
DEBUG = True
SECRET_KEY = 'DEVELOPMENT KEY'
USERNAME = 'admin'
PASSWORD = 'default'

# 
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
    """Returns a new connection to the database."""
    return MySQLdb.connect(host=DATABASE_HOST, user=DATABASE_USERNAME,\
                          passwd=DATABASE_PASSWORD, db=DATABASE_DB, charset='utf8')

def init_db():
    """Creates the database tables."""
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().execute(f.read())
        db.commit()

@app.before_request
def before_request():
    """Make sure we are connected to the database each request."""
    g.db = connect_db().cursor()

@app.teardown_request
def teardown_request(exception):
    """Close the database again at the end of the request."""
    if hasattr(g, 'db'):
        g.db.close()

@app.route('/')
def show_index():
    g.db.execute('select id_tag, slug, name from tag;')
    tags = [dict(id_tag=row[0], slug=row[1], name=row[2]) for row in g.db.fetchall()]
    return render_template('index.html', tags=tags)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_index'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0')
