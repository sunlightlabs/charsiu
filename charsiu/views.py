from django.views.generic import FormView, RedirectView, TemplateView
from django.http import Http404
from django.core.cache import cache
from django.conf import settings
from django import forms

from form_utils.forms import BetterForm
import json, urllib2, urlparse, datetime
import lxml.html

from charsiu.charsiu_extras.models import Survey

# index
class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        ctx = {}
        surveys = Survey.objects.all().order_by('completed', 'skipped', 'id')
        filter_param = self.request.GET.get('filter', None)
        if filter_param and ":" in filter_param:
            filter_parts = filter_param.split(":")
            print filter_parts
            surveys = [survey for survey in surveys if survey.field_match(filter_parts[0], filter_parts[1])]
            
            ctx['filter_name'] = filter_parts[0]
            ctx['filter_value'] = filter_parts[1]
        
        ctx.update({
            'surveys': surveys,
            'fields': [{
                'name': "response__" + k,
                'label': v.label,
                'choices': v.choices + (
                    [('None', '[no response]')] if not v.required else []
                )
            } for k, v in CommentForm().fields.items() if type(v) in (forms.ChoiceField, forms.MultipleChoiceField)] + \
                [{'name': 'response__flag', 'label': "Flag for further review", 'choices': (('True', 'Yes'),)}]
        })

        return ctx

# comment viewer/survey
class CommentForm(BetterForm):
    submitter_info = forms.ChoiceField(
        widget = forms.RadioSelect,
        label = 'Describe the submitter of this comment:',
        choices = (
            ('from_company', 'This comment was submitted by or on behalf of one or more organizations or companies'),
            ('from_official', 'This comment was submitted by one or more elected officials'),
            ('from_notable', 'This comment was submitted by one or more otherwise-notable individuals (describe in notes)'),
            ('other', 'Other'),
            ('unsure', "Can't tell")
        )
    )

    # entity ID/name fields
    entity_info = forms.ChoiceField(
        widget = forms.RadioSelect(attrs={'data-textbox-mapping': json.dumps({'in_ie':'entity_id','not_in_ie':'entity_name'})}),
        required = False,
        label = 'If applicable, which company/companies or official(s), and is it/are they in Influence Explorer?',
        choices = (
            ('in_ie', 'They are in Influence Explorer and ID(s) or URL(s) are (one per line if multiple):'),
            ('not_in_ie', 'They are not in Influence Explorer and their names are (one per line if multiple):'),
        )
    )
    entity_id = forms.CharField(widget=forms.Textarea(attrs={'rows':2, 'cols':80, 'style': 'width:auto;'}), required=False)
    entity_name = forms.CharField(widget=forms.Textarea(attrs={'rows':2, 'cols':80, 'style': 'width:auto;'}), required=False)

    # entity source
    entity_source = forms.MultipleChoiceField(
        widget = forms.CheckboxSelectMultiple(attrs={'data-textbox-mapping': json.dumps({'other':'entity_source_other'})}),
        required = False,
        label = 'If applicable, how do you know which official or company submitted the comment? (select all relevant answers)',
        choices = (
            ('in_submitter_meta', "Its name is in the document's submitter metadata (please annotate with tag \"submitter\")"),
            ('in_comment_title', 'Its name is in the comment title (please annotate with tag "submitter")'),
            ('in_comment_text', 'Its name is in the comment text (please annotate with tag "submitter")'),
            ('other', 'Other (please specify)'),
        )
    )
    entity_source_annotation = forms.CharField(widget=forms.HiddenInput(), required=False)
    entity_source_other = forms.CharField(widget=forms.Textarea(attrs={'rows':2, 'cols':80, 'style': 'width:auto;'}), required=False)

    # classification questions
    sentiment = forms.ChoiceField(
        widget = forms.RadioSelect,
        label = "Describe this commenter's sentiment with respect to the rulemaking:",
        choices = (
            ('negative_rule', 'This commenter expresses a negative sentiment about the rule'),
            ('negative_general', 'This commenter expresses a negative sentiment, but not about the rule'),

            ('negative_parts', 'This commenter expresses a negative sentiment about parts of the rule, but their overall sentiment is not explicitly positive or negative'),
            ('neutral', 'This commenter expresses both positive and negative sentiments about parts of the rule, but their overall sentiment is not explicitly positive or negative'),
            ('positive_parts', 'This commenter expresses a positive sentiment about parts of the rule, but their overall sentiment is not explicitly positive or negative'),

            ('positive_rule', 'This commenter expresses a positive sentiment about the rule'),
            ('positive_general', 'This commenter expresses a positive sentiment, but not about the rule'),
            ('unsure', "Can't tell"),
        )
    )

    sentiment_basis = forms.MultipleChoiceField(
        widget = forms.CheckboxSelectMultiple,
        label = 'If applicable, describe the basis on which the commenter expressed their criticism:',
        choices = (
            ('questons_info', "This commenter questions the adequacy and accuracy of information presented in the rule"),
            ('new_info', "This commenter presents new information relevant to the analysis done in the rule"),
            ('new_alternative', "This commenter presents reasonable alternatives to those presented in the rule"),
            ('revisions', "This commenter presents revisions of some of the material in the rule"),
            ('none', 'No basis'),
            ('unsure', "Can't tell"),
        ),
        required=False
    )


    substantiveness = forms.ChoiceField(
        widget = forms.RadioSelect,
        label = 'Describe the substantiveness of the comment:',
        choices = (
            ('substantive', "This commenter's statements are within the scope of the proposed action, are specific to the proposed action, have a direct relationship to the proposed action and include supporting reasons"),
            ('values', "This commenter expresses an a view that's not substantiated"),
            ('neither', 'Neither'),
            ('unsure', "Can't tell"),
        )
    )

    topic = forms.MultipleChoiceField(
        widget = forms.CheckboxSelectMultiple,
        label = 'Describe the predominant topic of this comment:',
        choices = (
            ('policy', "Policy arguments or discussion"),
            ('values', "Values"),
            ('science', "Scientific reasoning"),
            ('tech', "Technical expertise"),
            ('none', 'None of the above'),
            ('unsure', "Can't tell"),
        )
    )

    big_small_government = forms.ChoiceField(
        widget = forms.RadioSelect,
        label = 'Describe the perspective this comment expresses about government:',
        choices = (
            ('big_gov_specific', 'This comment advocates government intervention in this policy area'),
            ('big_gov_general', 'This comment advocates government intervention non-specifically'),
            ('small_gov_specific', 'This comment opposes government intervention in this policy area'),
            ('small_gov_general', 'This comment opposes government intervention generally'),
            ('other', 'Other'),
            ('unsure', "Can't tell"),
        )
    )

    # misc
    notes = forms.CharField(label="Additional notes", widget=forms.Textarea(attrs={'cols':80, 'style': 'width:auto;'}), required=False)
    flag = forms.BooleanField(label="Flag for further review", required=False)
    main_view = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        fieldsets = [
            ('entities', {'fields': ['submitter_info', 'entity_info', 'entity_id', 'entity_name', 'entity_source', 'entity_source_annotation', 'entity_source_other'], 'legend': 'Submitter Information'}),
            ('classification', {'fields': ['sentiment', 'sentiment_basis', 'substantiveness', 'topic', 'big_small_government'], 'legend': 'Classification'}),
            ('misc', {'fields': ['notes', 'flag', 'main_view'], 'legend': 'Additional Information'})
        ]
        row_attrs = {'entity_id': {'skip': True}, 'entity_name': {'skip': True}, 'entity_source_other': {'skip': True}}

DW_ROOT = getattr(settings, "DW_ROOT", "http://docketwrench.sunlightfoundation.com/")
API_KEY = getattr(settings, "API_KEY", "")
class CommentView(FormView):
    template_name = "comment.html"
    form_class = CommentForm

    def get(self, *args, **kwargs):
        self.document_id = kwargs['document_id']
        return super(CommentView, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        self.document_id = kwargs['document_id']
        return super(CommentView, self).post(*args, **kwargs)

    def get_initial(self):
        self.document = json.load(urllib2.urlopen(DW_ROOT + "api/1.0/document/%s?apikey=%s" % (self.document_id, API_KEY)))
        previous = list(Survey.objects.filter(id=self.document_id))
        if previous and previous[0].response:
            return previous[0].response
        else:
            se = [e for e in self.document.get('submitter_entities', []) if e['type'] == 'organization']
            if se:
                return {'entity_source': ['in_submitter_meta'], 'entity_info': u'in_ie', 'entity_id': "http://www.influenceexplorer.com" + se[0]['url'], 'from_company': 'yes', 'from_official': 'no'}
            else:
                return {}

    def get_context_data(self, **kwargs):
        ctx = super(CommentView, self).get_context_data(**kwargs)
        
        ctx['document'] = self.document
        ctx['submitter'] = dict(dict(ctx['document']['clean_details']).get('Submitter Information', []))
        ctx['combined_attachments'] = [{'title': 'Main Views', 'views': realize_views(ctx['document']['views'])}] + \
            [{'title': 'Attachment: ' + at['title'], 'views': realize_views(at['views'])} for at in ctx['document']['attachments']]

        ctx['doc_types'] = {'proposed_rule': 'Proposed Rule', 'other': 'Other', 'rule': 'Rule', 'notice': 'Notice'}

        return ctx

    def form_valid(self, form):
        previous = list(Survey.objects.filter(id=self.document_id))
        survey = previous[0] if previous else Survey()

        survey.response = form.cleaned_data
        survey.id = self.document_id
        survey.completed = True
        
        if not survey.history:
            survey.history = []
        survey.history.append({'date': datetime.datetime.now(), 'username': self.request.user.username})

        survey.save()

        return super(CommentView, self).form_valid(form)

    def get_success_url(self):
        if 'continue' in self.request.GET:
            return '/next'
        else:
            return '/'

class NextView(RedirectView):
    permanent = False
    def get_redirect_url(self):
        next = list(Survey.objects.filter(completed=False, skipped=False).order_by('?')[:1])
        if next:
            return '/comment/' + next[0].id
        else:
            return '/'

class SkipView(NextView):
    def get_redirect_url(self, document_id):
        surveys = list(Survey.objects.filter(id=document_id))
        if surveys:
            survey = surveys[0]
            survey.skipped = True
            survey.save()
        return super(SkipView, self).get_redirect_url()

# download and slightly mangle the views
def realize_views(views):
    for view in views:
        if view['extracted']:
            html = urllib2.urlopen(urlparse.urljoin(DW_ROOT, view['html'])).read()
            doc = lxml.html.fromstring(html)
            view['body'] = u"".join([lxml.html.tostring(n, encoding=unicode) for n in doc.body]) if doc.findall("body") else ""
            view['styles'] = doc.head.findall("style") if doc.findall("head") else []
    return views