from django.contrib import admin
from qset.models import Question, Set, Subject


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('type', 'subject', 'creation_date', 'creator', 'is_used')
    list_filter = ['creation_date']
    search_fields = ['text']
    date_hierarchy = 'creation_date'

admin.site.register(Question, QuestionAdmin)
admin.site.register(Set)
admin.site.register(Subject)
