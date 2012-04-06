#coding:utf8
from django.shortcuts import render_to_response
from models import Article

def index(request, template_name='blog/index.html'):
    articles = Article.objects.all()
    context = {
        'articles':articles,
    }
    return render_to_response(template_name, context)
