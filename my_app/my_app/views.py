import requests
import requests.auth

from django.http import HttpResponse, HttpRequest, JsonResponse
from django.urls import reverse
from django.views.generic.base import TemplateView, View
from django.views.decorators.cache import never_cache

from my_app.lib.ttam_api.ttam_api.django.views import AuthenticatedMixin as TtamAuthenticatedMixin
from my_app.lib.ttam_api.ttam_api.django.views import LogoutView as TtamLogoutView

import json, base64, requests

CLIENT_ID = '228JF7'
CLIENT_SECRET = '188fe570134d6630e372c8cff3cac04f'

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


class FitbitHandlerView(View):

    def get(self, request):
        print(self)
        print(request)
        print(request.GET)

        # body_unicode = request.body.decode('utf-8')
        # print('body_unicode' + body_unicode)
        # body = json.loads(body_unicode)
        # print('body' + body)
        # code = body['code']
        # print('got a code: ', code)

        try:
            code = request.GET['code']
        except KeyError:
            return print('no code in request parameter')

        print("got a code! " + code)

        print('construct a request')

        token = get_token(code)
        print(token)

        # persist token and show user
    
        return JsonResponse({'status': 'not authenticated'})



def get_token(code):
    # client_auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    auth_header = "Bearer " + str(base64.b64encode(("%s:%s" % (CLIENT_ID, CLIENT_SECRET)).encode('ascii')))
    post_data = {"grant_type": "authorization_code",
                 "code": code,
                 "client_id": CLIENT_ID,
                 "expires_in": 3*24*3600}
    headers = {"Authorization": auth_header}
    url = "https://api.fitbit.com/oauth2/token"
    response = requests.post(url, headers=headers, data=post_data)
    print("response for get token was:" + response.text)
    token_json = response.json()
    return token_json["access_token"]

@never_cache
def status(request):
    return HttpResponse('Status: OK')
