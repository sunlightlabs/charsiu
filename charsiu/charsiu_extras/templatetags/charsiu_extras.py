from django import template

register = template.Library()

# from http://djangosnippets.org/snippets/1412/
@register.filter
def get(dict, key, default = ''):
    """
    Usage: 

    view: 
    some_dict = {'keyA':'valueA','keyB':{'subKeyA':'subValueA','subKeyB':'subKeyB'},'keyC':'valueC'}
    keys = ['keyA','keyC']
    template: 
    {{ some_dict|get:"keyA" }}
    {{ some_dict|get:"keyB"|get:"subKeyA" }}
    {% for key in keys %}{{ some_dict|get:key }}{% endfor %}
    """
    print dict
    print key
    try:
        return dict.get(key, default)
    except:
        return default

@register.filter
def survey_status(survey):
    if survey.completed:
        return "completed"
    elif survey.skipped:
        return "skipped"
    else:
        return "ready"
