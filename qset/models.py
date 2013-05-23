from django.db import models
from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from usermanage.models import Group
import random
from hashlib import sha1

# Create your models here.

SUBJECT_CHOICES = (
    ('A', 'Astronomy'),
    ('B', 'Biology'),
    ('C', 'Chemistry'),
    ('E', 'Energy'),
    ('ES', 'Earth Science'),
    ('GG', 'Ocean Geography'),
    ('GL', 'Ocean Geology'),
    ('M', 'Math'),
    ('MB', 'Marine Biology'),
    ('MP', 'Marine Policy'),
    ('OC', 'Ocean Chemistry'),
    ('P', 'Physics'),
    ('PO', 'Physical Oceanography'),
    ('SS', 'Ocean History'),
    ('T', 'Technology'),
)
SUBJECT_CHOICES_DICT = {
    'ES': 'Earth Sci',
    'A': 'Astro',
    'P': 'Phys',
    'C': 'Chem',
    'M': 'Math',
    'B': 'Bio',
    'E': 'Energy',
    'OC': 'Ocean Chem',
    'PO': 'Physical O.',
    'MB': 'Marine Bio',
    'T': 'O. Tech',
    'MP': 'Marine Policy',
    'GL': 'O. Geology',
    'GG': 'O. Geography',
    'SS': 'O. History',
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

    def get_short_name(self):
        return SUBJECT_CHOICES_DICT[self.name]


class Question(models.Model):
    creator = models.ForeignKey(User)
    subject = models.ForeignKey(Subject)
    group = models.ForeignKey(Group, blank=True, null=True)
    type = models.IntegerField(choices=QUESTION_SUBTYPE_CHOICES, default=0)
    creation_date = models.DateTimeField(auto_now_add=True)
    # is_used:
    #   0: unused
    #   1: used
    #   2: holding
    is_used = models.IntegerField(default=0)
    text = models.CharField(max_length=500)
    choice_w = models.CharField(max_length=100, blank=True)
    choice_x = models.CharField(max_length=100, blank=True)
    choice_y = models.CharField(max_length=100, blank=True)
    choice_z = models.CharField(max_length=100, blank=True)
    answer = models.CharField(max_length=100)
    uid = models.CharField(max_length=200, unique=True)

    class Meta:
        ordering = ['-creation_date']

    def __unicode__(self):
        return "(" + self.subject.__str__() + ") " + self.creator.__str__()

    def save(self, *args, **kwargs):
        if self.uid is None or self.uid == "":
            key = hex(random.getrandbits(32)).rstrip("L").lstrip("0x")
            while Question.objects.filter(uid=key).count() > 0:
                key = hex(random.getrandbits(32)).rstrip("L").lstrip("0x")
            self.uid = key
        super(Question, self).save(*args, **kwargs)

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

    def get_view_url(self):
        return "/question/" + self.uid + "/"

    def get_edit_url(self):
        return "/question/edit/" + self.uid + "/"


class Set(models.Model):
    questions = models.ManyToManyField(Question, through='Set_questions')
    group = models.ForeignKey(Group, blank=True, null=True)
    name = models.CharField(max_length=100)
    subjects = models.ManyToManyField(Subject)
    description = models.CharField(max_length=1000)
    creation_date = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(User)
    is_used = models.BooleanField(default=False)
    uid = models.CharField(max_length=200, unique=True)

    def __unicode__(self):
        return self.description

    def save(self, *args, **kwargs):
        if self.uid is None or self.uid == "":
            uid = sha1(str(random.random())).hexdigest()
            while Set.objects.filter(uid=uid).count() > 0:
                uid = sha1(str(random.random())).hexdigest()
            self.uid = uid
        super(Set, self).save(*args, **kwargs)

    def get_view_url(self):
        return "/set/" + self.uid + "/"

    def get_edit_url(self):
        return "/set/edit/" + self.uid + "/"

    def has_bonus(self):
        return self.set_questions_set.filter(q_type=1).count() > 0


class SetForm(ModelForm):
    group = forms.ModelChoiceField(queryset=Group.objects.all(), help_text='Group to pull questions from')
    description = forms.CharField(max_length=200, widget=forms.Textarea, help_text='A meaningful description to differentiate from other sets.')
    num_questions = forms.IntegerField(min_value=1, max_value=100, label="Number of Questions")
    name = forms.CharField(help_text='A short name to identify the set.')
    subjects = forms.ModelMultipleChoiceField(queryset=Subject.objects.all(), help_text='Subjects covered by set. (Hold down "Ctrl" to select more than one)')
    toss_up = forms.BooleanField(label="Toss-Up Only")

    def __init__(self, user, *args, **kwargs):
        super(SetForm, self).__init__(*args, **kwargs)
        self.fields['group'].queryset = Group.objects.filter(membership__user=user, membership__status=1)
        if kwargs.get("instance", False):
            self.fields['num_questions'].initial = self.instance.questions.all().count()
            self.fields['toss_up'].initial = not self.instance.has_bonus()
            self.fields['group'].widget.attrs['disabled'] = True

    class Meta:
        model = Set
        exclude = ('uid', 'is_used', 'creation_date', 'creator', 'questions')


class Set_questions(models.Model):
    set = models.ForeignKey(Set)
    question = models.ForeignKey(Question)
    q_num = models.IntegerField()
    q_type = models.IntegerField(choices=QUESTION_TYPE_CHOICES)


class Round(models.Model):
    set = models.ForeignKey(Set)
    group = models.ForeignKey(Group)
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
        exclude = ('uid', 'is_used', 'creation_date', 'creator')

    def __init__(self, user, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        choices = user.group_set.all()
        self.fields['group'].queryset = choices
