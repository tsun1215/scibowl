from django.db import models
from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from qset.models import Subject
from usermanage.models import getAllUsers


class Author(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

    def __unicode__(self):
        return self.first_name + " " + self.last_name


class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(Author)
    pub_date = models.DateField()
    edition = models.IntegerField()
    checked_out_to = models.ForeignKey(User,  null=True,  blank=True)
    subject = models.ManyToManyField(Subject)

    def __unicode__(self):
        return self.title


class BookForm(ModelForm):
    author_first = forms.CharField(max_length=30)
    author_last = forms.CharField(max_length=30)
    subject = forms.ModelMultipleChoiceField(queryset=Subject.objects.all())

    class Meta:
        model = Book
        fields = ('title',  'author_first',  'author_last',  'pub_date',  'edition',  'subject', 'checked_out_to')

    def save(self, commit=True, *args, **kwargs):
        try:
            author = Author.objects.get(first_name=self.cleaned_data['author_first'], last_name=self.cleaned_data['author_last'])
        except Author.DoesNotExist:
            author = Author(first_name=self.cleaned_data['author_first'], last_name=self.cleaned_data['author_last'])
        author.save()
        b = Book(title=self.cleaned_data['title'], author=author, pub_date=self.cleaned_data['pub_date'], edition=self.cleaned_data['edition'], checked_out_to=self.cleaned_data['checked_out_to'])
        if not commit:
            return b
        super(Book,  b).save(*args, **kwargs)
        for subject in self.cleaned_data['subject']:
            b.subject.add(subject)

    def __init__(self, instance=None, *args, **kwargs):
        first = ""
        last = ""
        subjects = []
        if instance is not None:
            first = instance.author.first_name
            last = instance.author.last_name
            subjtemp = instance.subject.all()
            for subject in subjtemp:
                subjects += [str(subject.id)]
            super(ModelForm, self).__init__(instance=instance, initial=[('author_first', first), ('author_last', last), ('subject', subjects)], *args, **kwargs)
            return
        super(ModelForm, self).__init__(*args, **kwargs)


class CheckoutForm(forms.Form):
    user = forms.IntegerField(label="", widget=forms.Select(choices=getAllUsers(),  attrs={'class': 'user'}))
