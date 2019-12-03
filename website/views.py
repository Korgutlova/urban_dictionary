import datetime
import random
import time

from django import template
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.files.storage import FileSystemStorage
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.views.decorators.http import require_POST

from website.enums import STATUSES_FOR_REQUESTS

try:
    from django.utils import simplejson as json
except ImportError:
    import json

from website.forms import EditUserForm, EditProfileForm
from website.models import Definition, Term, CustomUser, Example, UploadData, Rating, RequestForPublication, Favorites

# Create your views here.
from django.views import View
from django.views.generic import ListView, DetailView

from website.models import Term, STATUSES, ROLE_CHOICES


def main_page(request):
    return render(request, 'website/main_page.html',
                  {'definitions': Definition.get_top_for_week})
    # {'definitions': Definition.objects.all})


def custom_handler404(request, exception):
    response = render_to_response("website/base/page_not_found.html")
    response.status_code = 404
    return response


@login_required
@transaction.atomic
def activate_user(request):
    request.user.custom_user.status = STATUSES[0][0]
    request.user.save()
    return redirect('website:update_profile')


@login_required
@require_POST
def change_password(request):
    password_form = PasswordChangeForm(user=request.user, data=request.POST)
    if password_form.is_valid():
        password_form.save()
        update_session_auth_hash(request, password_form.user)
        return redirect('website:main_page')
    else:
        request.session['change_password_msg'] = password_form.errors
        return redirect('website:update_profile')


@login_required
@transaction.atomic
def update_profile(request):
    password_form = PasswordChangeForm(user=request.user)
    if request.method == 'POST':
        user_form = EditUserForm(request.POST, instance=request.user)
        profile_form = EditProfileForm(request.POST, instance=request.user.custom_user)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            user = profile_form.save(commit=False)
            user.photo = request.FILES['photo']
            user.save()
            return redirect('website:main_page')
    else:
        user_form = EditUserForm(instance=request.user)
        profile_form = EditProfileForm(instance=request.user.custom_user)
        password_form._errors = request.session.pop('change_password_msg', None)
    return render(request, 'website/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'password_form': password_form,
        'role': ROLE_CHOICES[request.user.custom_user.role - 1][1]
    })


@login_required
def create_definition(request):
    current_user = CustomUser.objects.get(user=request.user)
    if request.method == 'POST':
        term = Term.objects.filter(name=request.POST["name"]).first()
        if term is None:
            term = Term(name=request.POST["name"])
            term.save()
        definition = Definition(term=term, description=request.POST["description"],
                                source=request.POST["source"],
                                author=current_user)
        definition.save()
        if current_user.is_moderator() or current_user.is_admin():
            definition.date = time.time()
            definition.save()
        else:
            rfp = RequestForPublication(definition=definition, date_creation=datetime.datetime.now())
            rfp.save()
        examples = request.POST.getlist("examples")
        primary = int(request.POST.get("primary"))
        for i, ex in enumerate(examples):
            example = Example(example=ex, primary=True if primary == i else False, definition=definition)
            example.save()
        for f, h in zip(request.FILES.getlist("upload_data"), request.POST.getlist("header")):
            link_file = "%s/%s/%s.%s" % (
                definition.author.id, definition.id, int(time.time() * 1000), f.name.split(".")[1])
            print(link_file)
            fs = FileSystemStorage()
            filename = fs.save(link_file, f)
            u = UploadData(header_for_file=h, definition=definition, image=filename)
            u.save()
        return redirect("website:definition", definition.id)
    return render(request, "website/definition/create_definition.html", {})


@login_required
def edit_definition(request, pk):
    definition = Definition.objects.get(id=pk)
    current_user = request.user.custom_user
    if definition.author != current_user:
        return redirect("website:page_not_found")
    rfp = RequestForPublication.objects.get(definition=definition)
    if request.method == "POST":
        # TO DO
        # NEED TO CHECK
        term = Term.objects.filter(name=request.POST["name"]).first()
        if term is None:
            term = Term(name=request.POST["name"])
            term.save()
        definition.term = term
        definition.description = request.POST["description"]
        definition.source = request.POST["source"],
        definition.save()
        if current_user.is_moderator() or current_user.is_admin():
            definition.date = time.time()
            definition.save()
        else:
            rfp.date_creation = datetime.datetime.now()
            rfp.status = STATUSES_FOR_REQUESTS[0][0]
            rfp.save()
        examples = request.POST.getlist("examples")
        primary = int(request.POST.get("primary"))
        for file in definition.files.all():
            file.delete()
        for example in definition.examples.all():
            example.delete()
        for i, ex in enumerate(examples):
            example = Example(example=ex, primary=True if primary == i else False, definition=definition)
            example.save()
        for f, h in zip(request.FILES.getlist("upload_data"), request.POST.getlist("header")):
            link_file = "%s/%s/%s.%s" % (
                definition.author.id, definition.id, int(time.time() * 1000), f.name.split(".")[1])
            print(link_file)
            fs = FileSystemStorage()
            filename = fs.save(link_file, f)
            u = UploadData(header_for_file=h, definition=definition, image=filename)
            u.save()
        return redirect("website:personal_definitions")
    return render(request, "website/definition/edit_definition.html", {"definition": definition, "rfp": rfp})


@login_required
def request_for_definition(request, pk):
    current_user = CustomUser.objects.get(user=request.user)
    rfp = get_object_or_404(RequestForPublication, pk=pk)
    if not current_user.is_admin() or not rfp.is_new():
        return redirect("website:page_not_found")
    if request.method == 'POST':
        answer = request.POST["answer"]
        if answer == "approve":
            rfp.status = STATUSES_FOR_REQUESTS[2][0]
            rfp.definition.date = datetime.datetime.now()
            rfp.definition.save()
        else:
            if answer == "reject":
                rfp.status = STATUSES_FOR_REQUESTS[1][0]
            else:
                rfp.status = STATUSES_FOR_REQUESTS[3][0]
            rfp.reason = request.POST["reason"]
        rfp.save()
        return redirect('website:requests_pub')

    return render(request, "website/admin/admin_definition_check.html", {"rfp": rfp})


def page_not_found(request):
    return render(request, "website/base/page_not_found.html", )


def definition(request, pk):
    return render(request, "website/definition/definition.html", {"definition": Definition.objects.get(id=pk)})


def personal_definitions(request):
    if request.user.is_authenticated:
        current_user = request.user.custom_user
        return render(request, "website/definition/personal_definitions.html",
                      {"definitions": Definition.objects.filter(author=current_user)})
    return redirect("website:page_not_found")


class TermView(View):

    def get(self, request, pk):
        term = Term.objects.get(pk=pk)
        return render(request, 'website/term_page.html',
                      {'term': term})


@require_POST
def like(request):
    if request.method == 'POST':
        user = request.user.custom_user
        definition_id = request.POST.get('def_id', None)
        defin = get_object_or_404(Definition, pk=definition_id)

        if defin.estimates.filter(user=user, estimate=1).exists():
            # user has already liked this definition
            # remove like/user
            defin.estimates.get(user=user).delete()
        elif defin.estimates.filter(user=user, estimate=0).exists():
            defin.estimates.get(user=user).delete()
            Rating(definition=defin, user=user, estimate=1).save()
        else:
            # add a new like for a company
            Rating(definition=defin, user=user, estimate=1).save()

        ctx = {'likes_count': defin.get_likes(), 'dislikes_count': defin.get_dislikes()}
        # use mimetype instead of content_type if django < 5
        return HttpResponse(json.dumps(ctx), content_type='application/json')


def dislike(request):
    if request.method == 'POST':
        user = request.user.custom_user
        definition_id = request.POST.get('def_id', None)
        defin = get_object_or_404(Definition, pk=definition_id)

        if defin.estimates.filter(user=user, estimate=0).exists():
            # user has already liked this definition
            # remove like/user
            defin.estimates.get(user=user).delete()
        elif defin.estimates.filter(user=user, estimate=1).exists():
            defin.estimates.get(user=user).delete()
            Rating(definition=defin, user=user, estimate=0).save()
        else:
            # add a new like for a company
            Rating(definition=defin, user=user, estimate=0).save()

        ctx = {'dislikes_count': defin.get_dislikes(), 'likes_count': defin.get_likes()}
        # use mimetype instead of content_type if django < 5
        return HttpResponse(json.dumps(ctx), content_type='application/json')


def favourite(request):
    if request.method == 'POST':
        user = request.user.custom_user
        definition_id = request.POST.get('def_id', None)
        defin = get_object_or_404(Definition, pk=definition_id)

        if defin.favorites.filter(user=user).exists():
            defin.favorites.get(user=user).delete()
            colour = 'black'
        else:
            Favorites(definition=defin, user=user).save()
            colour = 'red'

        ctx = {'colour': colour}
        return HttpResponse(json.dumps(ctx), content_type='application/json')


@login_required
def favourites(request):
    favs = Favorites.objects.filter(user=request.user.custom_user)
    result = [fav.definition for fav in favs]
    return render(request, 'website/main_page.html',
                  # {'definitions': Definition.get_top_for_week})
                  {'definitions': result})


def random_definition(request):
    definitons = [d for d in Definition.objects.all() if d.is_publish()]
    definition = random.choice(definitons)
    return redirect("website:definition", definition.id)


def search(request):
    query = request.GET.get('q')
    object_list = Definition.objects.filter(
        Q(description__icontains=query) | Q(term__name__icontains=query)
    )
    if object_list:
        return render(request, 'website/main_page.html',
                      {'definitions': object_list})
    else:
        return redirect("website:page_not_found")


def requests_pub(request):
    user = request.user.custom_user
    if user.is_admin():
        return render(request, 'website/admin/requests_for_publication.html',
                      {'rfps': RequestForPublication.objects.filter(status=STATUSES_FOR_REQUESTS[0][0])})
    return redirect("website:page_not_found")
