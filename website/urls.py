from django.conf.urls import url
from website.views import *

app_name = "website"

urlpatterns = [
    url(r'^$', HomePageView.as_view(), name='home_page'),
    url(r'^(?P<pk>\d+)$', TermView.as_view(), name='term_page'),
]