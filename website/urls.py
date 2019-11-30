from django.conf.urls import url
from website.views import *

app_name = "website"

urlpatterns = [
    url(r'^$', main_page, name="main_page"),
    url(r'^edit_profile/$', update_profile, name='update_profile'),
    url(r'^create_definition/$', page_create_definition, name='page_create_definition'),
    url(r'^definition/(?P<pk>\d+)$',  TermView.as_view(), name='definition'),
    url(r'^activate_user/$', activate_user, name='activate_user'),
]
