from django.db import models
from picklefield.fields import PickledObjectField
from charsiu.util import field_compare

class Survey(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    completed = models.BooleanField(default=False)
    history = PickledObjectField(default=[])
    response = PickledObjectField(default={})
    skipped = models.BooleanField(default=False)

    def field_match(self, fieldname, value):
        return field_compare(self.__dict__, fieldname, value)