from django.conf.urls import patterns, include, url
from charsiu.views import *

urlpatterns = patterns('',
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^comment/(?P<document_id>[A-Z0-9_-]+$)', CommentView.as_view(), name='comment'),
)
