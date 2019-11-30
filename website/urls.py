from django.urls import path
from website.views import *

app_name = "website"

urlpatterns = [
    path(r'', main_page, name="main_page"),
    path(r'edit_profile/', update_profile, name='update_profile'),
    path(r'create_definition/', page_create_definition, name='page_create_definition'),
    path(r'definition/<int:pk>',  TermView.as_view(), name='definition'),
    path(r'activate_user/', activate_user, name='activate_user'),
    path(r'definition/like', like, name='like'),
    path(r'definition/dislike', dislike, name='dislike'),
]
