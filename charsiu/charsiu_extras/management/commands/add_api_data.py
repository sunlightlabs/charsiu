from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from charsiu.charsiu_extras.models import Survey
from charsiu.views import CommentForm

import json, urllib2, random, os
from collections import OrderedDict, defaultdict

from django import forms

class Command(BaseCommand):
    help = 'Check entity match quality.'

    def handle(self, *args, **options):
        for survey in Survey.objects.all():
            if not survey.api_data:
                survey.api_data = json.load(urllib2.urlopen("http://docketwrench.sunlightfoundation.com/api/1.0/document/%s?format=json" % survey.id))
                print survey.id
                survey.save()