from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from charsiu.charsiu_extras.models import Survey

import json, urllib2, random

class Search(object):
    def __init__(self, query, exclude_docs, exclude_dockets):
        self.exclude_docs = exclude_docs
        self.exclude_dockets = exclude_dockets
        self.query = query

        self._page = None

    @property
    def page(self):
        if self._page == None:
            self._results = json.load(urllib2.urlopen("http://docketwrench.sunlightfoundation.com/api/1.0/search/document-non-fr/%s?limit=50&format=json" % self.query))
            self._page = self._results['results']
        elif self._page == []:
            if self._results['next']:
                self._results = json.load(urllib2.urlopen("http://docketwrench.sunlightfoundation.com" + self._results['next']))
                self._page = self._results['results']
        return self._page

    def next(self):
        while True:
            current_page = self.page
            if len(current_page) == 0:
                return None

            item = random.choice(current_page)
            current_page.remove(item)

            item_id = item['_id']
            docket_id = item_id.rsplit('-', 1)[0]
            if item_id in self.exclude_docs or docket_id in self.exclude_dockets:
                continue
            else:
                self.exclude_docs.add(item_id)
                self.exclude_dockets.add(docket_id)
                return item



class Command(BaseCommand):
    args = '<count>'
    help = 'Add new documents to the pool.'

    option_list = BaseCommand.option_list + (
        make_option(
            '--agency', '-a',
            action='store',
            dest='agency',
            default=None,
            help='Restrict to one agency.'
        ),
        make_option(
            '--practice',
            action='store_true',
            dest='practice',
            default=False,
            help="Don't actually do anything."
        ),
        make_option(
            '--term', '-t',
            action='append',
            dest='terms',
            help='Specify a search term.'
        )
    )

    def handle(self, *args, **options):
        count = int(args[0]) if args else 5

        terms = options['terms'] if options['terms'] else [""]
        terms = [" ".join(filter(bool, ["agency:%s" % options['agency'] if options['agency'] else False, "type:public_submission", term])) for term in terms]

        docs = set()
        dockets = set()

        for survey in Survey.objects.all():
            docs.add(survey.id)
            dockets.add(survey.id.rsplit("-", 1)[0])

        searches = [Search(term, docs, dockets) for term in terms]
        results = []

        # main search loop
        while True:
            search = random.choice(searches)
            next = search.next()
            if not next:
                searches.remove(search)
            else:
                try:
                    document = json.load(urllib2.urlopen("http://docketwrench.sunlightfoundation.com/api/1.0/document/%s?format=json" % next['_id']))
                except:
                    continue
                # if it doesn't have any views, or as any attachments that don't have any views, skip it
                if len(document['views']) == 0 or any([len(attachment['views']) == 0 for attachment in document['attachments']]):
                    print "Skipping %s because it's broken." % next['_id']
                else:
                    results.append(next)
                    print 'On search "%s", adding document %s' % (search.query, next['_id'])

            if len(results) >= count or len(searches) == 0:
                break

        if options['practice']:
            print "Practice mode; doing nothing."
        else:
            for result in results:
                s = Survey()
                s.id = result['_id']
                s.save()