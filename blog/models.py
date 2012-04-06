from django.db import models

class Article(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    publish_date = models.DateTimeField(auto_now=True)
