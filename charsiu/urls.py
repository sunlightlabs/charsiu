from django.conf.urls import patterns, include, url
from charsiu.views import *

from django.contrib.auth.decorators import login_required

urlpatterns = patterns('',
    url(r'^$', login_required(IndexView.as_view()), name='index'),
    url(r'^next$', login_required(NextView.as_view()), name='next'),
    url(r'^skip/(?P<document_id>[A-Z0-9_-]+$)', login_required(SkipView.as_view()), name='skip'),
    url(r'^comment/(?P<document_id>[A-Z0-9_-]+$)', login_required(CommentView.as_view()), name='comment'),

    # auth
    (r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login'),
)
