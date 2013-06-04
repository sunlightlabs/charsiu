from charsiu.charsiu_extras.models import Survey

def categories_to_checkbox():
    for survey in Survey.objects.filter(completed=True):
        if 'topic' in survey.response and type(survey.response['topic']) != list:
            print "Switching %s" % survey.id
            survey.response['topic'] = [survey.response['topic']]
            survey.save()