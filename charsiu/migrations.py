from charsiu.charsiu_extras.models import Survey

def categories_to_checkbox():
    for survey in Survey.objects.filter(completed=True):
        if 'topic' in survey.response and type(survey.response['topic']) != list:
            print "Switching %s" % survey.id
            survey.response['topic'] = [survey.response['topic']]
            survey.save()

def combine_submitter_info():
    for survey in Survey.objects.filter(completed=True):
        if survey.response['from_official'] == 'unsure' or survey.response['from_company'] == 'unsure':
            survey.response['submitter_info'] = 'unsure'
        elif survey.response['from_company'] == 'yes':
            survey.response['submitter_info'] = 'from_company'
        elif survey.response['from_official'] == 'yes':
            survey.response['submitter_info'] = 'from_official'
        else:
            survey.response['submitter_info'] = 'other'
        del survey.response['from_official']
        del survey.response['from_company']

        print survey.id, survey.response['submitter_info']
        survey.save()