from django.views.generic import FormView, RedirectView, TemplateView
from django.http import Http404
from django.core.cache import cache
from django.conf import settings
from django import forms

from form_utils.forms import BetterForm
import json, urllib2

# index
class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        return {}

# comment viewer/survey
class CommentForm(BetterForm):
    from_company = forms.ChoiceField(
        widget = forms.RadioSelect,
        label = 'Was this comment submitted by or on behalf of a company?',
        choices = (
            ('yes', 'Yes'),
            ('no', 'No'),
            ('unsure', "Can't tell")
        )
    )

    from_official = forms.ChoiceField(
        widget = forms.RadioSelect,
        label = 'Was this comment submitted by an elected official?',
        choices = (
            ('yes', 'Yes'),
            ('no', 'No'),
            ('unsure', "Can't tell")
        )
    )

    # entity ID/name fields
    entity_info = forms.ChoiceField(
        widget = forms.RadioSelect(attrs={'data-textbox-mapping': json.dumps({'in_ie':'entity_id','not_in_ie':'entity_name'})}),
        required = False,
        label = 'Which company or official, and is it/are they in Influence Explorer?',
        choices = (
            ('in_ie', 'The entity is in Influence Explorer and its ID or URL is:'),
            ('not_in_ie', 'The entity is not in Influence Explorer and its name is:'),
        )
    )
    entity_id = forms.CharField(required = False)
    entity_name = forms.CharField(required = False)

    # entity source
    entity_source = forms.MultipleChoiceField(
        widget = forms.CheckboxSelectMultiple(attrs={'data-textbox-mapping': json.dumps({'other':'entity_source_other'})}),
        required = False,
        label = 'How do you know which official or company submitted the comment? (select all relevant answers)',
        choices = (
            ('in_submitter_meta', "Its name is in the document's submitter metadata"),
            ('in_comment_title', 'Its name is in the comment title (please annotate)'),
            ('in_comment_text', 'Its name is in the comment text (please annotate)'),
            ('other', 'Other (please specify)'),
        )
    )
    entity_source_annotation = forms.CharField(widget=forms.HiddenInput(), required=False)
    entity_source_other = forms.CharField(required=False)

    # classification questions
    sentiment = forms.ChoiceField(
        widget = forms.RadioSelect,
        label = "Describe this commenter's sentiment with respect to the rulemaking:",
        choices = (
            ('negative_rule', 'This commenter expresses a negative sentiment about the rule'),
            ('negative_general', 'This commenter expresses a negative sentiment, but not about the rule'),
            ('positive_rule', 'This commenter expresses a positive sentiment about the rule'),
            ('positive_general', 'This commenter expresses a positive sentiment, but not about the rule'),
            ('neutral', 'This commenter expresses a sentiment that is neither explicitly positive nor negative'),
            ('unsure', "Can't tell"),
        )
    )


    substantiveness = forms.ChoiceField(
        widget = forms.RadioSelect,
        label = 'Describe the substantiveness of the comment:',
        choices = (
            ('substantive', "This commenter makes expresses a substantive view that's supported by underlying data or facts"),
            ('values', "This commenter expresses an emotional view that's not substantiated"),
            ('neither', 'Neither'),
            ('unsure', "Can't tell"),
        )
    )

    # classification questions
    big_small_government = forms.ChoiceField(
        widget = forms.RadioSelect,
        label = 'Describe the perspective this comment expresses about government:',
        choices = (
            ('big_gov_specific', 'This comment advocates government intervention in this policy area'),
            ('big_gov_general', 'This comment advocates government intervention non-specifically'),
            ('small_gov_specific', 'This comment opposes government intervention in this policy area'),
            ('positive_general', 'This comment opposes government intervention generally'),
            ('other', 'Other'),
            ('unsure', "Can't tell"),
        )
    )

    # misc
    notes = forms.CharField(label="Additional notes", widget=forms.Textarea(attrs={'cols':80, 'style': 'width:auto;'}), required=False)
    flag = forms.BooleanField(label="Flag for further review", required=False)
    main_view = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        fieldsets = [
            ('entities', {'fields': ['from_company', 'from_official', 'entity_info', 'entity_id', 'entity_name', 'entity_source', 'entity_source_annotation', 'entity_source_other'], 'legend': 'Submitter Information'}),
            ('classification', {'fields': ['sentiment', 'substantiveness', 'big_small_government'], 'legend': 'Classification'}),
            ('misc', {'fields': ['notes', 'flag', 'main_view'], 'legend': 'Additional Information'})
        ]
        row_attrs = {'entity_id': {'skip': True}, 'entity_name': {'skip': True}, 'entity_source_other': {'skip': True}}

DW_ROOT = getattr(settings, "DW_ROOT", "http://docketwrench.sunlightfoundation.com/")
class CommentView(FormView):
    template_name = "comment.html"
    success_url = 'http://www.google.com'
    form_class = CommentForm

    def get(self, *args, **kwargs):
        self.document_id = kwargs['document_id']
        return super(CommentView, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(CommentView, self).get_context_data(**kwargs)
        
        ctx['document'] = json.load(urllib2.urlopen(DW_ROOT + "api/1.0/document/%s" % self.document_id))
        ctx['submitter'] = dict(dict(ctx['document']['clean_details']).get('Submitter Information', []))

        return ctx