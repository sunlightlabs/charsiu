from charsiu.charsiu_extras.models import Survey

def import_file(filename):
    for sline in open(filename, "r"):
        line = sline.strip()
        if line:
            s = Survey()
            s.id = line
            s.save()