from django.http import HttpResponse
from django.shortcuts import render


# Create your views here.
from django.views import View
from django.views.generic import ListView, DetailView

from website.models import Term


class HomePageView(ListView):
    model = Term
    context_object_name = 'terms'
    template_name = 'website/homepage.html'

    # def get_page(self):
    #     page = 1
    #     if 'page' in self.kwargs:
    #         page = int(self.kwargs['page'])
    #     return page
    #
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['total'] = Term.objects.count()
    #     context['page'] = self.get_page()
    #     return context


class TermView(View):

    def get(self, request, pk):
        term = Term.objects.get(pk=pk)
        return render(request, 'website/term_page.html',
                      {'term': term,
                       })