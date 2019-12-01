from django.urls import path
from website.views import *

app_name = "website"

urlpatterns = [
    path(r'', main_page, name="main_page"),
    path(r'edit_profile/', update_profile, name='update_profile'),
    path(r'create_definition/', create_definition, name='create_definition'),
    path(r'term/<int:pk>',  TermView.as_view(), name='term'),
    path(r'activate_user/', activate_user, name='activate_user'),
    path(r'personal_definitions/', personal_definitions, name='personal_definitions'),
    path(r'definition/<int:pk>', definition, name='definition'),
    path(r'definition/check/<int:pk>', request_for_definition, name='request_for_definition'),
    path(r'page_not_found/', page_not_found, name='page_not_found'),
    path(r'definition/like', like, name='like'),
    path(r'definition/dislike', dislike, name='dislike'),
    path(r'favourite/', favourite, name='favourite'),
    path(r'favourites/', favourites, name='favourites_list'),
]
