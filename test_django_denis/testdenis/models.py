from django.db import models
from django.contrib.auth.models import User


class School(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    desctiption = models.TextField()

    def __unicode__(self):
        return self.name


class Class(models.Model):
    name = models.CharField(max_length=255)
    school = models.ForeignKey(School)
    year = models.IntegerField()

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Classes"


class Student(models.Model):
    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    user = models.OneToOneField(User)
    fclass = models.ForeignKey(Class)

    def __unicode__(self):
        return self.surname


class Teacher(models.Model):
    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    enable = models.BooleanField(default=False)
    user = models.OneToOneField(User)
    fclass = models.ManyToManyField(Class, through='Course')

    def __unicode__(self):
        return self.surname


class Course(models.Model):
    DISCIPLINE_CHOICES = (
        ('E', u'English'),
        ('M', u'Math'),
        ('H', u'History')
    )

    discipline = models.CharField(max_length=1, choices=DISCIPLINE_CHOICES)
    teacher = models.ForeignKey(Teacher)
    fclass = models.ForeignKey(Class)

    def __unicode__(self):
        return self.get_discipline_display()
