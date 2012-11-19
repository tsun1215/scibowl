from django.db import models
from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User

# Create your models here.

SUBJECT_CHOICES = (
    ('ES', 'Earth Science'),
    ('A', 'Astronomy'),
    ('P', 'Physics'),
    ('C', 'Chemistry'),
    ('M', 'Math'),
    ('B', 'Biology'),
    ('E', 'Energy'),
    ('OC', 'Chemistry (NOSB)'),
    ('PO', 'Physical Oceanography(NOSB)'),
    ('MB', 'Marine Biology (NOSB)'),
    ('T', 'Technology (NOSB)'),
    ('MP', 'Marine Policy (NOSB)'),
    ('GL', 'Geology (NOSB)'),
    ('GG', 'Geography (NOSB)'),
    ('SS', 'Social Sciences (NOSB)'),
)
SUBJECT_CHOICES_DICT = {
    'ES': 'Earth Science',
    'A': 'Astronomy',
    'P': 'Physics',
    'C': 'Chemistry',
    'M': 'Math',
    'B': 'Biology',
    'E': 'Energy',
    'OC': 'Chemistry (NOSB)',
    'PO': 'Physical Oceanography (NOSB)',
    'MB': 'Marine Biology (NOSB)',
    'T': 'Technology (NOSB)',
    'MP': 'Marine Policy (NOSB)',
    'GL': 'Geology (NOSB)',
    'GG': 'Geography (NOSB)',
    'SS': 'Social Sciences (NOSB)',
}
QUESTION_TYPE_CHOICES = (
    (0, 'Multiple Choice'),
    (1, 'Short Answer'),
)
SCORE_TYPES_CHOICES = (
    ('c', 'Correct'),
    ('w', 'Incorrect'),
    ('ic', 'Correct Interupt'),
    ('iw', 'Incorrect Interupt'),
    ('b', 'Blurt'),
)


class Subject(models.Model):
    name = models.CharField(max_length=3, choices=SUBJECT_CHOICES)

    def __unicode__(self):
        return self.get_name_display()


class Question(models.Model):
    creator = models.ForeignKey(User)
    subject = models.ForeignKey(Subject)
    type = models.IntegerField(choices=QUESTION_TYPE_CHOICES, default=0)
    creation_date = models.DateTimeField(auto_now=True)
    is_used = models.BooleanField(default=False)
    text = models.CharField(max_length=500)
    choice_w = models.CharField(max_length=100, blank=True)
    choice_x = models.CharField(max_length=100, blank=True)
    choice_y = models.CharField(max_length=100, blank=True)
    choice_z = models.CharField(max_length=100, blank=True)
    answer = models.CharField(max_length=100)

    class Meta:
        ordering = ['-creation_date']

    def __unicode__(self):
        return "(" + self.subject.__str__() + ") " + self.creator.__str__()


class Set(models.Model):
    questions = models.ManyToManyField(Question, through='Set_questions')
    description = models.CharField(max_length=100)
    creation_date = models.DateTimeField()
    creator = models.ForeignKey(User)
    is_used = models.BooleanField(default=False)

    def __unicode__(self):
        return self.description


class Set_questions(models.Model):
    set = models.ForeignKey(Set)
    question_id = models.ForeignKey(Question)
    q_num = models.IntegerField()


class Round(models.Model):
    set = models.ForeignKey(Set)
    date = models.DateField()
    players = models.ManyToManyField(User)


class Score(models.Model):
    round = models.ForeignKey(Round)
    question = models.ForeignKey(Set_questions)
    player = models.ForeignKey(User)
    score = models.CharField(max_length=2, choices=SCORE_TYPES_CHOICES)
    score_val = models.IntegerField()


class QuestionForm(ModelForm):
    text = forms.CharField(max_length=500, widget=forms.Textarea)
    choice_w = forms.CharField(max_length=100, label='W', required=False)
    choice_x = forms.CharField(max_length=100, label='X', required=False)
    choice_y = forms.CharField(max_length=100, label='Y', required=False)
    choice_z = forms.CharField(max_length=100, label='Z', required=False)

    class Meta:
        model = Question
        exclude = ('is_used', 'creation_date', 'creator')
