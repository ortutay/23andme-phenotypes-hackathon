import requests
import requests.auth

from django.http import HttpResponse, HttpRequest, JsonResponse
from django.urls import reverse
from django.views.generic.base import TemplateView, View
from django.views.decorators.cache import never_cache
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import redirect

from my_app.lib.ttam_api.ttam_api.django.views import AuthenticatedMixin as TtamAuthenticatedMixin
from my_app.lib.ttam_api.ttam_api.django.views import LogoutView as TtamLogoutView

from my_app.my_app import utils
from my_app.my_app.models import Profile

import json
import base64
import requests

from my_app.my_app import facebook


CLIENT_ID = '228JF7'
CLIENT_SECRET = '188fe570134d6630e372c8cff3cac04f'


class Index(TtamAuthenticatedMixin, TemplateView):
    template_name = 'index/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #import pdb; pdb.set_trace()
        context = super().get_context_data(**kwargs)
        #self.request.ttam.api.account
        accession_id = 'NC_000004.11'
        context['accession'] = self.request.ttam.api.get(
            f'/3/accession/{accession_id}/'
            # params={'querystring': 'params', 'go': 'here'},
            # data={'data': 'goes here'}
        )
        context['first_name'] = self.request.ttam.account['first_name']
        context['last_name'] = self.request.ttam.account['last_name']

        # this should probably go somewhere else. oh well!
        try:
            user = User.objects.get(email=self.request.ttam.account['email'])
            print('Found user', user)
        except User.DoesNotExist:
            print('Making a new user')
            print('23andMe token:', self.request.ttam.api.access_token)
            user = User(
                first_name=self.request.ttam.account['first_name'],
                last_name=self.request.ttam.account['last_name'],
                email=self.request.ttam.account['email'],
                username=self.request.ttam.account['email'],
                password='password')
            user.save()
            user.profile = Profile()
            user.profile.ttam_token = self.request.ttam.api.access_token
            user.profile.save()
        if not self.request.user.is_authenticated():
            login(self.request, user)

        phenotype_ids = [
            'facebook_images_avg_people',
            'facebook_posts_personality_agreeableness',
            'facebook_posts_personality_conscientiousness',
            'facebook_posts_personality_emotional',
            'facebook_posts_personality_extraversion',
            'facebook_posts_personality_openness',
        ]
        phenotypes = utils.get_phenotypes(user.profile.ttam_token, phenotype_ids)
        context['phenotypes'] = phenotypes
        # print(phenotypes)

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
        print("does the request have a user?")
        print(request.user)

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

        token = get_token(code)
        print(token)

        profile = get_profile(token)
        print(profile)
        # get interesting data from fitbit

        return JsonResponse({'status': 'request went through'})

def get_profile(token):

    url = 'https://api.fitbit.com/1/user/-/profile.json'

    auth_header = "Bearer " + (base64.b64encode(("%s" % (token)).encode('ascii')).decode('ascii'))
    headers = {"Authorization": auth_header}
    print(headers)
    print("response for get token was:" + response.text)
    r = requests.get(url, headers=headers)
    print(r.status_code)
    print(r.headers)
    print(r.encoding)
    print(r.text)
    print(r.json())


def get_token(code):
    # client_auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    auth_header = "Basic " + (base64.b64encode(("%s:%s" % (CLIENT_ID, CLIENT_SECRET)).encode('ascii')).decode('ascii'))
    post_data = {"grant_type": "authorization_code",
                 "code": code,
                 "client_id": CLIENT_ID,
                 "redirect_uri": "https://localhost:5000/fitbit-handler",
                 "expires_in": 3*24*3600}
    headers = {"Authorization": auth_header}
    print(headers)
    url = "https://api.fitbit.com/oauth2/token"
    response = requests.post(url, headers=headers, data=post_data)
    print("response for get token was:" + response.text)
    token_json = response.json()
    return token_json["access_token"]


class FacebookHandlerView(View):
    def get(self, request):
        access_token = request.GET['access_token']
        user_id = request.GET['user_id']
        print(request.user)
        request.user.profile.facebook_token = access_token
        request.user.profile.save()
        fb_phenos = facebook.process(request.user.profile.facebook_token)
        for id, val in fb_phenos.items():
            print('set pheno', id, val)
            utils.set_phenotype(request.user.profile.ttam_token, id, val)
        return redirect('/')


@never_cache
def status(request):
    return HttpResponse('Status: OK')
