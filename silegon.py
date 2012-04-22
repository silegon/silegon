#!/usr/bin/env python
#coding=utf-8
import MySQLdb
import datetime
import markdown
from docutils.core import publish_parts

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
    g.db.execute("select title, publish_date, content_html from post where content_status='P';")
    context = [dict(title=row[0], publish_date=row[1], content_html=row[2])\
               for row in g.db.fetchall()]
    return render_template('index.html',c=context)

content_format_dict = {
    'raw':'R',
    'rst':'S',
    'md':'M',
}
content_status_dict = {
    'publish':'P',
    'draft':'D',
    'hide':'H',
}
@app.route('/new_article', methods=['GET', 'POST'])
def new_article():
    error = None
    if request.method == 'POST':
        f = request.form
        title = f.get('title', None)
        slug = f.get('slug', None)
        content = f.get('content', None)
        _format = f.get('format', None)
        _status = f.get('status', None)
        format = content_format_dict[_format]
        if format == 'R':
            content_html = content
        elif format == 'S':
            content_html = publish_parts(content, writer_name='html')['body']
        elif format == 'M':
            content_html = markdown.markdown(content)
        else:
            abort(401)
        status = content_status_dict[_status]
        publish_date = datetime.date.today()
        g.db.execute("insert into post (title, slug, content, content_html,\
                     content_format, content_status, publish_date) values \
                     ('%s','%s','%s','%s','%s','%s','%s')"%\
                    (title, slug, content, content_html,\
                     format, status, publish_date)) 
    context = {
        'format':'R',
        'status':'P',
    }
    return render_template('article_form.html', c=context, error=error)


#@app.route('/edit_article', methods=['GET', 'POST'])
#def edit_article():
#    error = None
#    if request.method == 'POST':
#        pass
#    return render_template('article_form.html', error=error)

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
