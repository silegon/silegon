#!/usr/bin/env python
#coding=utf-8
import MySQLdb
import math
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

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

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

def all_tags():
    g.db.execute("select id_tag, slug, name, count from tag;")
    tags = [dict(id_tag=row[0], slug=row[1] or 'id'+str(row[0]), name=row[2], 
                        count=row[3])for row in g.db.fetchall()]
    for tag in tags:
        tag['size'] = math.sqrt(tag['count']/3+1)*8
    return tags

def add_post_tag(tag_name, id_post):
    g.db.execute("insert into tag set name='%s' on duplicate key\
                 update count=count+1;"%(tag_name))
    g.db.execute("select id_tag from tag where name='%s';"%(tag_name))
    id_tag = g.db.fetchone()[0]
    g.db.execute("insert into tag_post(id_tag, id_post) values \
                 (%s, %s);"%(id_tag, id_post))

def remove_post_tag(tag_name, id_post):
    g.db.execute("select id_tag from tag where name='%s';"%(tag_name))
    id_tag = g.db.fetchone()[0]
    g.db.execute("delete from tag_post where id_post=%s and id_tag=%s;"%(id_post, id_tag))
    g.db.execute("select count from tag where id_tag=%s"%(id_tag))
    tag_count = g.db.fetchone()[0]
    if tag_count==1:
        g.db.execute("delete from tag where id_tag=%s"%(id_tag))
    else:
        g.db.execute("update tag set count=count-1 where id_tag=%s;"%(id_tag)) 

def get_post_tags(id_post):
    g.db.execute("select tag.id_tag, slug, name, count from tag, tag_post where \
                 tag_post.id_post=%s and tag.id_tag=tag_post.id_tag; "%(id_post))
    post_tags = [dict(id_tag=row[0], slug=row[1] or 'id'+str(row[0]), name=row[2], 
                    count=row[3])for row in g.db.fetchall()]
    return post_tags

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
    g.db.execute("select id_post, title, slug, publish_date, content_html \
                 from post where content_status='P';")
    context = [dict(id_post=row[0], title=row[1], slug=row[2],
                    publish_date=row[3], content_html=row[4]) 
               for row in g.db.fetchall()]
    for post in context:
        post['tag'] = get_post_tags(post['id_post'])
    return render_template('index.html', c=context, all_tags=all_tags())

@app.route('/post/<post_slug>')
def show_post(post_slug):
    if post_slug.startswith('id'):
        id_post = post_slug[2:]
        g.db.execute("select id_post, title, publish_date, content_html, slug from \
                     post where id_post=%s;"%(id_post))
    else:
        g.db.execute("select id_post, title, publish_date, content_html, slug from \
                     post where slug='%s';"%(post_slug))
    try:
        post_row = g.db.fetchone()
        post = dict(id_post=post_row[0], title=post_row[1], publish_date=post_row[2],
                  content_html=post_row[3], slug=post_row[4] or 'id'+post_row[0])
        post.tag = get_post_tags['id_post']
    except:
        pass
    return render_template('show_post.html', post=post, all_tags=all_tags()) 

@app.route('/new_post', methods=['GET', 'POST'])
def new_post():
    if not session.get('logged_in'):
        abort(401)
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
        if title and content_html:
            g.db.execute("insert into post (title, slug, content, content_html,\
                     content_format, content_status, publish_date) values \
                     ('%s','%s','%s','%s','%s','%s','%s')"%\
                    (title, slug, content, content_html,\
                     format, status, publish_date)) 
            g.db.execute("select last_insert_id();")
            id_post = g.db.fetchone()[0]
            #######for tags ######
            _tag = f.get('tag', None)
            if _tag:
                tags = _tag.split()
                for tag_name in tags:
                    add_post_tag(tag_name, id_post)
    context = {
        'format':'R',
        'status':'P',
    }
    return render_template('post_form.html', c=context, error=error)

@app.route('/tag/<tag_slug>')
def tag_ref_post(tag_slug):
    if tag_slug.startswith('id'):
        id_tag = tag_slug[2:]
    else:
        g.db.execute("select id_tag from tag where slug='%s';"%(tag_slug))
        try:
            id_tag = g.db.fetchone()[0]
        except:
            abort (401)
    g.db.execute("select post.id_post, title, slug, publish_date \
                 from post,tag_post where tag_post.id_tag=%s and \
                 tag_post.id_post=post.id_post and post.content_status='P';"%(id_tag))
    context = [dict(id_post=row[0], title=row[1], slug=row[2],
                     publish_date=row[3]) for row in g.db.fetchall()]
    g.db.execute("select name, count, slug from tag where id_tag=%s"%(id_tag))
    tag_row = g.db.fetchone()
    tag = dict(name=tag_row[0], count=tag_row[1], slug=tag_row[2] or 'id'+id_tag)
    return render_template('tag_ref_post.html', c=context, tag=tag) 
                 
#@app.route('/edit_post', methods=['GET', 'POST'])
#def edit_post():
#    error = None
#    if request.method == 'POST':
#        pass
#    return render_template('post_form.html', error=error)

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
