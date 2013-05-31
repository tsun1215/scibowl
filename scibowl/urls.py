from django.conf.urls import patterns, include, url
from django.contrib.auth.views import login, logout
from django.views.generic import TemplateView

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
    url(r'', include('social_auth.urls')),
    url(r'^login/$', 'django.contrib.auth.views.login', {"template_name": "usermanage/login.html"}),
    url(r'^register/$', 'usermanage.views.registerUser'),
    url(r'^logout/$', logout, {'next_page': '/'}),
    url(r'^account/info/edit', 'usermanage.views.editInfo'),
    url(r'^question/add/', 'qset.views.addQuestion'),
    url(r'^account/questions/', 'qset.views.filterQuestions'),
    url(r'^group/(?P<group_id>[a-zA-Z0-9]+)/questions/$', 'qset.views.filterQuestions'),
    url(r'^question/edit/(?P<q_id>[a-zA-Z0-9]+)', 'qset.views.editQuestion'),
    url(r'^question/delete/(?P<q_id>[a-zA-Z0-9]+)', 'qset.views.removeQuestion'),
    url(r'^ajax/getq/$', 'qset.views.getQuestions'),
    url(r'^ajax/(?P<group_id>[a-zA-Z0-9]+)/getq/$', 'qset.views.getQuestions'),
    url(r'^home/$', TemplateView.as_view(template_name="home.html")),
    url(r'^$', TemplateView.as_view(template_name="home.html")),
    url(r'^close/$', TemplateView.as_view(template_name="close.html")),
    url(r'^set/add/$', 'qset.views.addSet'),
    url(r'^set/edit/(?P<set_id>[a-zA-Z0-9]+)', 'qset.views.editSet'),
    url(r'^account/sets/$', 'qset.views.listSets'),
    url(r'^set/(?P<set_id>[a-zA-Z0-9]+)/$', 'qset.views.viewSet'),
    url(r'^set/(?P<set_id>[a-zA-Z0-9]+)/pdf/$', 'qset.views.setToPDF'),
    url(r'^ajax/moveq/$', 'qset.views.addQuestionToGroup'),
)

urlpatterns += patterns('usermanage.views',
    url(r'^account/groups/$', 'listGroups'),    
    url(r'^account/info/edit', 'editInfo'),
    url(r'^group/create/$', 'createGroup'),
    url(r'^group/delete/(?P<group_id>[a-zA-Z0-9]+)/$', 'deleteGroup'),
    url(r'^ajax/group/(?P<group_id>[a-zA-Z0-9]+)/(?P<user_id>[a-zA-Z0-9]+)/$', 'addUserToGroup'),
    url(r'^ajax/group/remove/(?P<group_id>[a-zA-Z0-9]+)/(?P<user_id>[a-zA-Z0-9]+)/$', 'removeUserFromGroup'),
    url(r'^group/(?P<group_id>[a-zA-Z0-9]+)/$', 'viewGroup'),
    url(r'^group/edit/(?P<group_id>[a-zA-Z0-9]+)/$', 'editGroup'),
    url(r'^group/perms/(?P<group_id>[a-zA-Z0-9]+)/$', 'editGroupPerms'),
)
