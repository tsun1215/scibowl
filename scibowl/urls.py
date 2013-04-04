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

    url(r'^login/', login, {'template_name': 'usermanage/login.html'}),
    url(r'^logout/', logout, {'next_page': '/'}),
    url(r'^question/add/', 'qset.views.addQuestion'),
    url(r'^question/list/', 'qset.views.filterQuestions'),
    url(r'^question/edit/(?P<q_id>[a-zA-Z0-9]+)', 'qset.views.editQuestion'),
    url(r'^question/delete/(?P<q_id>[a-zA-Z0-9]+)', 'qset.views.removeQuestion'),
    url(r'^getall/$', 'qset.views.getQuestions'),
    url(r'^home/$', TemplateView.as_view(template_name="home.html")),
    url(r'^account/questions/$', TemplateView.as_view(template_name="home.html")),
    url(r'^$', TemplateView.as_view(template_name="home.html")),
    url(r'^set/add/$', 'qset.views.addSet'),
    url(r'^set/edit/(?P<set_id>[a-zA-Z0-9]+)', 'qset.views.editSet'),
    url(r'^account/sets/$', 'qset.views.listSets'),
    url(r'^set/(?P<set_id>[a-zA-Z0-9]+)/$', 'qset.views.viewSet'),
    url(r'^ajax/moveq/$', 'qset.views.addQuestionToGroup'),
)

urlpatterns += patterns('usermanage.views',
    url(r'^ajax/login/$', 'ajaxLogin'),
    url(r'^register/$', 'registerUser'),
    url(r'^account/group/$', 'listGroups'),
    url(r'^group/create/$', 'createGroup'),
    url(r'^ajax/group/(?P<group_id>[a-zA-Z0-9]+)/(?P<user_id>[a-zA-Z0-9]+)/$', 'addUserToGroup'),
    url(r'^group/(?P<group_id>[a-zA-Z0-9]+)/$', 'viewGroup'),
    url(r'^group/edit/(?P<group_id>[a-zA-Z0-9]+)/$', 'editGroup'),
    url(r'^group/perms/(?P<group_id>[a-zA-Z0-9]+)/$', 'editGroupPerms'),
)
