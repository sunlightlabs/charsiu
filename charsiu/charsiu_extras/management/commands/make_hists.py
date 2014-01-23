from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from charsiu.charsiu_extras.models import Survey
from charsiu.views import CommentForm

import json, urllib2, random, os
from collections import OrderedDict, defaultdict

from django import forms

import matplotlib.pyplot as plt
import numpy as np

class Command(BaseCommand):
    args = '<output directory>'
    help = 'Make histograms of stuff.'

    def handle(self, *args, **options):
        output_dir = args[0]

        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        sample = CommentForm()
        fields = defaultdict(list)

        for label, field in sample.fields.items():
            if type(field) in (forms.ChoiceField, forms.MultipleChoiceField):
                for choice in field.choices:
                    fields[label].append(choice[0])

        totals = defaultdict(lambda: defaultdict(int))

        # assemble histogram data
        for survey in Survey.objects.filter(completed=True):
            for field in fields.keys():
                if field in survey.response:
                    field_responses = survey.response[field] if type(survey.response[field]) is list else [survey.response[field]]
                    for field_response in field_responses:
                        totals[field][field_response] += 1

        # make histograms
        for field, choices in sorted(fields.items()):
            print "==============\n"
            print "Short label:", field
            print "Question:", sample.fields[field].label
            print "Responses:"
            field_totals = [totals[field][choice] for choice in choices]

            for item in zip(choices, [f[1] for f in sample.fields[field].choices]):
                print " = ".join(item)
            print ""

            fig = plt.figure()
            ax = plt.subplot(111)

            width = 0.8

            ax.bar(range(len(choices)), field_totals, width=width)
            ax.tick_params(axis='x', labelsize='small')
            ax.set_xticks(np.arange(len(choices)) + width/2)
            ax.set_xticklabels(choices, rotation=20)
            plt.savefig(os.path.join(output_dir, field + '.png'))