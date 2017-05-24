from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.views.generic.base import TemplateView, View
from django.views.decorators.cache import never_cache

from my_app.lib.ttam_api.ttam_api.django.views import AuthenticatedMixin as TtamAuthenticatedMixin
from my_app.lib.ttam_api.ttam_api.django.views import LogoutView as TtamLogoutView


class Index(TtamAuthenticatedMixin, TemplateView):
    template_name = 'index/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        accession_id = 'NC_000004.11'
        context['accession'] = self.request.ttam.api.get(
            f'/3/accession/{accession_id}/'
            # params={'querystring': 'params', 'go': 'here'},
            # data={'data': 'goes here'}
        )
        context['first_name'] = self.request.ttam.account['first_name']
        context['last_name'] = self.request.ttam.account['last_name']
        return context


class AuthenticatedStatus(View):

    def get(self, request):
        if request.session.get('ttam_account_id'):
            return JsonResponse({
                'status': 'authenticated',
                'ttam_account_id': request.session['ttam_account_id'],
            })
        else:
            return JsonResponse({'status': 'not authenticated'})


class LogoutView(TtamLogoutView):

    def get_redirect_url(self, request, url_name=None):
        return request.build_absolute_uri(reverse('index'))


@never_cache
def status(request):
    return HttpResponse('Status: OK')
