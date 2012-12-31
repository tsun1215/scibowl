from django.db import models
from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User

# Create your models here.

SUBJECT_CHOICES = (
    ('A', 'Astronomy'),
    ('B', 'Biology'),
    ('C', 'Chemistry'),
    ('E', 'Energy'),
    ('ES', 'Earth Science'),
    ('GG', 'Geography (NOSB)'),
    ('GL', 'Geology (NOSB)'),
    ('M', 'Math'),
    ('MB', 'Marine Biology (NOSB)'),
    ('MP', 'Marine Policy (NOSB)'),
    ('OC', 'Chemistry (NOSB)'),
    ('P', 'Physics'),
    ('PO', 'Physical Oceanography(NOSB)'),
    ('SS', 'Social Sciences (NOSB)'),
    ('T', 'Technology (NOSB)'),
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
QUESTION_SUBTYPE_CHOICES = (
    (0, 'Multiple Choice'),
    (1, 'Short Answer'),
)
QUESTION_TYPE_CHOICES = (
    (0, 'TOSS-UP'),
    (1, 'BONUS'),
)
SCORE_TYPES_CHOICES = (
    ('c', 'Correct'),
    ('w', 'Incorrect'),
    ('ic', 'Correct Interrupt'),
    ('iw', 'Incorrect Interrupt'),
    ('b', 'Blurt'),
)


class Subject(models.Model):
    name = models.CharField(max_length=3, choices=SUBJECT_CHOICES)

    def __unicode__(self):
        return self.get_name_display()


class Question(models.Model):
    creator = models.ForeignKey(User)
    subject = models.ForeignKey(Subject)
    type = models.IntegerField(choices=QUESTION_SUBTYPE_CHOICES, default=0)
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

    def ans(self):
        if self.type == 1:
            return self.answer
        else:
            if self.answer.strip().lower() == "w":
                return "W) " + self.choice_w
            if self.answer.strip().lower() == "x":
                return "X) " + self.choice_x
            if self.answer.strip().lower() == "y":
                return "Y) " + self.choice_y
            if self.answer.strip().lower() == "z":
                return "Z) " + self.choice_z


class Set(models.Model):
    questions = models.ManyToManyField(Question, through='Set_questions')
    subjects = models.ManyToManyField(Subject)
    description = models.CharField(max_length=100)
    creation_date = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(User)
    is_used = models.BooleanField(default=False)

    def __unicode__(self):
        return self.description


class SetForm(ModelForm):
    description = forms.CharField(max_length=200, widget=forms.Textarea)
    num_questions = forms.IntegerField()

    class Meta:
        model = Set
        exclude = ('is_used', 'creation_date', 'creator', 'questions')


class Set_questions(models.Model):
    set = models.ForeignKey(Set)
    question = models.ForeignKey(Question)
    q_num = models.IntegerField()
    q_type = models.IntegerField(choices=QUESTION_TYPE_CHOICES)


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
