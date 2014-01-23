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
        # all the surveys submitted by IE entities where an entity is tagged
        surveys = Survey.objects.filter(completed=True)

        print surveys
        full_match = 0
        partial_match = 0
        no_match = 0
        false_positives = 0
        match_potential = 0
        for survey in surveys:
            if survey.response.get('entity_info', None) == 'in_ie' and survey.response['entity_id']:
                record = {
                    'id': survey.id,
                    'entities': [url.split('/')[-1].strip() for url in survey.response['entity_id'].split('\n')]
                }
                confirmed = set(record['entities'])
                detected = set([e['id'] for e in survey.api_data['submitter_entities']])
                if confirmed == detected:
                    print "full", survey.id, confirmed, detected
                    full_match += 1
                elif len(confirmed.intersection(detected)) > 0:
                    print "partial", survey.id, confirmed, detected
                    partial_match += 1
                else:
                    print "no", survey.id, confirmed, detected
                    no_match += 1

                    mentioned = set([e['id'] for e in survey.api_data['text_entities']])
                    if len([eid for eid in confirmed if eid in mentioned]) > 0:
                        print "YES"
                        match_potential += 1
            elif survey.response.get('entity_info', None) != 'in_ie':
                if survey.response.get('entity_id', None):
                    print "fp", survey.id
                    false_positives += 1


        print "Full match:", full_match
        print "Partial match:", partial_match
        print "No match:", no_match
        print "Match potential:", match_potential
        print 'Total in IE:', full_match + partial_match + no_match
        print "False positives:", false_positives