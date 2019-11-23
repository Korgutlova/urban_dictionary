from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect

from website.forms import EditUserForm, EditProfileForm

# Create your views here.
from django.views import View
from django.views.generic import ListView, DetailView

from website.models import Term


class HomePageView(ListView):
    model = Term
    context_object_name = 'terms'
    template_name = 'website/homepage.html'

def main_page(request):
    return render(request, "base/base_page.html", {})


@login_required
@transaction.atomic
def update_profile(request):
    if request.method == 'POST':
        user_form = EditUserForm(request.POST, instance=request.user)
        profile_form = EditProfileForm(request.POST, instance=request.user.custom_user)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('website:main_page')
    else:
        user_form = EditUserForm(instance=request.user)
        profile_form = EditProfileForm(instance=request.user.custom_user)
    return render(request, 'edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


class TermView(View):

    def get(self, request, pk):
        term = Term.objects.get(pk=pk)
        return render(request, 'website/term_page.html',
                      {'term': term,
                       })