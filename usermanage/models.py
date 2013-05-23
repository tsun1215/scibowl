from django.db import models
from django import forms
from django.contrib.auth.models import User
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


class InfoEditForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('first_name', 'last_name')


class RegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=30)
    first_name = forms.CharField(max_length=30, error_messages={'required': '\"First name\" cannot be left blank'})
    last_name = forms.CharField(max_length=30, error_messages={'required': '\"Last name\" cannot be left blank'})
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput, error_messages={'required': 'Password cannot be left bank'})
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput, error_messages={'required': 'Please retype your password'})

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def clean_email(self):
        if User.objects.filter(email=self.cleaned_data.get("email")).count() > 0:
            raise forms.ValidationError("Already an account under this email")
        return self.cleaned_data.get("email")

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


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
