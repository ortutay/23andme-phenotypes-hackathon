import json
from collections import namedtuple

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.views.generic import View
from django.shortcuts import redirect
from django.utils.cache import add_never_cache_headers

from .. import exceptions
from ..django import client

CURRENT_PROFILE_ID = 'ttam_current_profile_id'
Ttam = namedtuple('Ttam', ['account', 'current_profile', 'api'])


class OauthCallbackView(View):

    def get(self, request):
        if client.authenticate(request) is None:
            return redirect(client.login_url(request))
        state = json.loads(request.GET.get('state', '{}'))
        origin_uri = state.get('origin_uri', '/')
        if not origin_uri.startswith('/') or origin_uri.startswith('//'):
            raise ValueError('%s is a non-relative redirect path!' % origin_uri)
        return redirect(origin_uri)


def _get_api(request):
    access_token, refresh_token = client.get_tokens(request)
    if access_token and refresh_token:
        oauth_client = client.get(
            access_token=access_token,
            refresh_token=refresh_token)
        return oauth_client
    return None


def _get_account(api):
    accounts = api.get('/3/account/', params={'include': 'profiles'})
    account = accounts['data'][0]
    account['owned_human_ids'] = set(human['id'] for human in account['profiles'])
    # Account is valid if we're here. It may have 0 or more profiles.
    current_profile = account['profiles'][0]
    return account, current_profile


class AuthenticatedMixin(object):
    """Mixin to ensure a client is oauth authenticated. Redirects to api login if not."""

    def _response_for_no_auth(self, request):
        """Handle no-auth behavior for views that we want to force authentication for."""
        if request.is_ajax():
            return HttpResponse('Unauthorized', status=401)
        return redirect(client.login_url(request))

    def dispatch(self, request, *args, **kwargs):
        request.ttam = Ttam
        api = _get_api(request)
        if api is None:
            return self._response_for_no_auth(request)

        try:
            account, current_profile = _get_account(api)
        except exceptions.UnauthenticatedException:
            return self._response_for_no_auth(request)

        request.ttam = Ttam(api=api, account=account, current_profile=current_profile)
        request.session['ttam_account_id'] = account['id']
        try:
            response = super().dispatch(request, *args, **kwargs)

            # Tell browser not to cache authenticated pages
            add_never_cache_headers(response)

            return response
        except AttributeError:
            # if extending the mixin, you may not want to call the parent view's dispatch yet
            return None


class LogoutView(View):

    def dispatch(self, request, *args, **kwargs):
        request.session.flush()
        return super(LogoutView, self).dispatch(request, *args, **kwargs)

    def get_redirect_url(self, request, url_name=None):
        if url_name:
            return request.build_absolute_uri(reverse(url_name))
        if 'redirect_uri' in request.GET:
            return request.build_absolute_uri(request.GET['redirect_uri'])
        return request.build_absolute_uri('/')

    def get_api_url(self, redirect_url):
        return '{api_url}/logout/?redirect_uri={redirect_url}'.format(
            api_url=settings.API_URL,
            redirect_url=redirect_url)

    def get(self, request):
        redirect_url = self.get_redirect_url(request)
        return redirect(self.get_api_url(redirect_url))


class ProfileSwitcherView(AuthenticatedMixin, View):

    def get(self, request):
        profile_id = request.GET.get('profile-id')
        redirect_uri = request.GET.get('redirect-uri') or 'home'
        request.session[CURRENT_PROFILE_ID] = profile_id
        return redirect(redirect_uri)
