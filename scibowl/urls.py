from django.conf.urls import patterns, include, url
from django.contrib.auth.views import login, logout

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'scibowl.views.home', name='home'),
    # url(r'^scibowl/', include('scibowl.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    #url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    url(r'^login/', login, {'template_name': 'usermanage/login.html'}),
    url(r'^logout/', logout, {'next_page': '/'}),
    url(r'^question/add/', 'qset.views.addQuestion'),
    url(r'^question/edit/(?P<q_id>\d+)', 'qset.views.editQuestion'),
    url(r'^getall/$', 'qset.views.getQuestions'),
    url(r'^register/$', 'usermanage.views.registerUser'),
)

urlpatterns += patterns('bookkeeping.views',
    url(r'^book/add', 'addBook'),
    url(r'^book/edit/(?P<book_id>\d+)', 'editBook'),
)
