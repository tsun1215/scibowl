from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
import re
import random


class Group(models.Model):
    name = models.CharField(max_length=100)
    creator = models.ForeignKey(User, related_name='+')
    description = models.CharField(max_length=2000)
    users = models.ManyToManyField(User, through="Membership")
    creation_date = models.DateTimeField(auto_now_add=True)
    uid = models.CharField(max_length=200, unique=True)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.uid is None or self.uid == "":
            key = hex(random.getrandbits(32)).rstrip("L").lstrip("0x")
            while Group.objects.filter(uid=key).count() > 0:
                key = hex(random.getrandbits(32)).rstrip("L").lstrip("0x")
            self.uid = key
        super(Group, self).save(*args, **kwargs)

    def admins(self):
        return User.objects.filter(group=self, membership__status=1).exclude(pk=self.creator.pk)

    def reg_users(self):
        return User.objects.filter(group=self, membership__status=0).exclude(pk=self.creator.pk)

    def all_users(self):
        return User.objects.filter(group=self).exclude(membership__status=2)

    def pending(self):
        return User.objects.filter(group=self, membership__status=2).exclude(pk=self.creator.pk)

    def get_short_descrip(self):
        tot_length = 70
        return self.description[:tot_length] + "..." if len(self.description) > tot_length else self.description

    def get_view_url(self):
        return "/group/" + self.uid + "/"

    def get_edit_url(self):
        return "/group/edit/" + self.uid + "/"

    def get_perms_url(self):
        return "/group/perms/" + self.uid + "/"


class GroupCreateForm(forms.ModelForm):
    description = forms.CharField(max_length=2000, widget=forms.Textarea)

    class Meta:
        model = Group
        fields = ("name", "description")


class Membership(models.Model):
    group = models.ForeignKey(Group)
    user = models.ForeignKey(User)
    status = models.IntegerField(default=2)
    # Change to "status"
    # 0: normal user
    # 1: staff
    # 2: pending user

    def is_staff(self):
        return self.status == 1

    def get_remove_url(self):
        return "/ajax/group/remove/" + self.group.uid + "/" + self.user.id.__str__() + "/"


class UserCreateForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    username = forms.CharField(help_text="")
    password2 = forms.CharField(help_text="", widget=forms.PasswordInput, label="Retype Password")

    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(UserCreateForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

    def clean_email(self):
        data = self.cleaned_data['email']
        if User.objects.filter(email=data).count() > 0:
            raise forms.ValidationError("There is an account under that email already")
        return data

    def clean_first_name(self):
        data = self.cleaned_data['first_name']
        if not re.match(r'^[A-Za-z\-\.]+$', data):
            raise forms.ValidationError("That is not a valid name")
        return data

    def clean_last_name(self):
        data = self.cleaned_data['last_name']
        if not re.match(r'^[A-Za-z\-\.]+$', data):
            raise forms.ValidationError("That is not a valid name")
        return data


class AdminAuthForm(AuthenticationForm):
    def clean(self):
        u = self.cleaned_data.get('username')
        p = self.cleaned_data.get('password')
        us = authenticate(username=u, password=p)
        if us is not None and not us.is_staff:
            self._errors['notadmin'] = True
            raise forms.ValidationError("You are not authorized to view this page")
        AuthenticationForm.clean(self)


def getAllUsers():
    userlist = [('', '---')]
    try:
        for user in User.objects.filter(is_superuser=False, is_active=True):
            if user.first_name:
                userlist += [(user.id, user.first_name + " " + user.last_name + " (" + user.username + ")")]
            else:
                userlist += [(user.id, user.username)]
    except Exception:
        pass
    return userlist
