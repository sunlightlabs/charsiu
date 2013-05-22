from django.views.generic import FormView, RedirectView, TemplateView
from django.http import Http404
from django.core.cache import cache
from django.conf import settings
from django import forms

from form_utils.forms import BetterForm

# index
class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        return {}

# comment viewer/survey
class CommentForm(BetterForm):
    from_company = forms.ChoiceField(
        label = 'Was this comment submitted by or on behalf of a company?',
        choices = (
            ('yes', 'Yes'),
            ('no', 'No'),
            ('unsure', "Can't tell")
        )
    )

    from_official = forms.ChoiceField(
        label = 'Was this comment submitted by an elected official?',
        choices = (
            ('yes', 'Yes'),
            ('no', 'No'),
            ('unsure', "Can't tell")
        )
    )

    # entity ID/name fields
    entity_info = forms.ChoiceField(
        label = 'Which company or official, and is it/are they in Influence Explorer?',
        choices = (
            ('in_ie', 'The entity is in Influence Explorer and its ID or URL is:'),
            ('not_in_ie', 'The entity is not in Influence Explorer and its name is:'),
        )
    )
    entity_id = forms.CharField()
    entity_name = forms.CharField()

    # entity source
    entity_source = forms.ChoiceField(
        label = 'How do you know which official or company submitted the comment?',
        choices = (
            ('in_submitter_meta', "Its name is in the document's submitter metadata"),
            ('in_comment_title', 'Its name is in the comment title (please annotate)'),
            ('in_comment_text', 'Its name is in the comment text (please annotate)'),
            ('other', 'Other (please specify)'),
        )
    )
    entity_source_annotation = forms.CharField()
    entity_source_other = forms.CharField()

    # classification questions
    sentiment = forms.ChoiceField(
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


    substantive = forms.ChoiceField(
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
    notes = forms.CharField()
    flag = forms.BooleanField()
    main_view = forms.CharField()


class CommentView(FormView):
    template_name = "comment.html"
    success_url = 'http://www.google.com'
    form_class = CommentForm