from django.conf.urls import url
from website.views import *

app_name = "website"

urlpatterns = [
    url(r'^$', main_page)
]