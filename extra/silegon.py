#!/usr/bin/env python
#coding=utf-8
from __future__ import with_statement
from flask import Flask, request, session, redirect, url_for, render_template
from datetime import datetime
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://root:root@localhost/silegon'
db = SQLAlchemy(app)

TagPost = db.Table('tag_post',
    db.Column(db.Integer, db.ForeignKey('tag.id'), index=True),
    db.Column(db.Integer, db.ForeignKey('post.id'), index=True)
)
    
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.title(80))
    title = db.Column(db.String(80))
    body = db.Column(db.Text)
    tags = db.relationship('Tag', secondary=TagPost,
                           backref=db.backgref('posts', lazy='dynamic'))

    def __init__(self, title, body, slug, pub_date=None):
        self.title = title
        self.body = body
        self.slug = slug
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date

    def __repr__(self):
        return '<Post %r>' % self.title

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(20), unique=True)
    name = db.Column(db.String(20), unique=True)
    posts = db.relationship('Post', secondary=TagPost,
                            backref=db.backgref('tags', lazy='dynamic'))

    def __init__(self, slug, name):
        self.slug = slug
        self.name = name

    def __repr__(self):
        return '<Tag %r>' % self.name


