def import_file(filename):
    from charsiu.charsiu_extras.models import Survey
    for sline in open(filename, "r"):
        line = sline.strip()
        if line:
            s = Survey()
            s.id = line
            s.save()

def field_compare(object, fieldname, value):
    if "__" in fieldname:
        fieldname_parts = fieldname.split("__", 1)
        field = object.get(fieldname_parts[0], None)
        if field:
            return field_compare(field, fieldname_parts[1], value)
        else:
            return False
    else:
        field = object.get(fieldname, None)
        if not field:
            return False
        if type(field) in (tuple, dict, list):
            return value in field
        else:
            return field == value