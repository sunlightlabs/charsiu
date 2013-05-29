from django.db import models
from picklefield.fields import PickledObjectField

class Survey(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    completed = models.BooleanField(default=False)
    history = PickledObjectField(default=[])
    response = PickledObjectField(default={})
    skipped = models.BooleanField(default=False)