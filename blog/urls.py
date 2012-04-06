#coding:utf-8
from django.conf.urls import patterns, url
from blog import views

urlpatterns = patterns('',
    url('', views.index),
)
