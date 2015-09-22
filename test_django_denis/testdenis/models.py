from django.db import models

class EvenMoreData(models.Model):
    name = models.CharField(max_length=255)

class SomeData(models.Model):
    name = models.CharField(max_length=255)
    evenmore = models.ManyToManyField(EvenMoreData)

class SomeMoreData(models.Model):
    somedata = models.ForeignKey(SomeData)
