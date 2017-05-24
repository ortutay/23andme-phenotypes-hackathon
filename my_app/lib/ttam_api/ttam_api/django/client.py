import json
from six.moves import urllib

from django.conf import settings
from django.shortcuts import redirect

from oauthlib.oauth2 import InvalidRequestError
from requests.exceptions import HTTPError
from requests_oauthlib import OAuth2Session

from ..oauth_client import client


def get(access_token=None, refresh_token=None):
    return client.OauthClient(
        access_token=access_token,
        refresh_token=refresh_token,
        client_id=settings.API_CLIENT_ID,
        client_secret=settings.API_CLIENT_SECRET,
        scope=settings.API_SCOPE,
        api_url=settings.API_URL,
        debug=settings.DEBUG,
        verify=settings.CERT_FILE)


def get_tokens(request):
    """Returns a (access_token, refresh_token) tuple iff both are set in the session"""
    try:
        return request.session['access_token'], request.session['refresh_token']
    except KeyError:
        return None, None


def set_tokens(request, access_token, refresh_token):
    request.session['access_token'] = access_token
    request.session['refresh_token'] = refresh_token


def _get_callback_uri(request):
    if request.is_secure():
        scheme = 'https://'
    else:
        scheme = 'http://'
    return scheme + request.get_host() + settings.API_REDIRECT_PATH


def login_url(request):
    auth_params = {
        'redirect_uri': _get_callback_uri(request),
        'response_type': 'code',
        'client_id': settings.API_CLIENT_ID,
        'scope': settings.API_SCOPE,
        'skip_buy_page': 1,
        'internal_login': 1,
        'state': json.dumps({
            'origin_uri': request.get_full_path()
        })
    }
    return urllib.parse.urljoin(settings.API_URL, '/authorize/') + '?' + urllib.parse.urlencode(auth_params)


def redirect_to_login(request):
    request.session.flush()
    return redirect(login_url(request))


def authenticate(request):
    try:
        auth_code = request.GET['code']
        oauth_client = _new_session(
            authorization_code=auth_code,
            redirect_uri=_get_callback_uri(request))
    except (KeyError, InvalidRequestError):
        return None
    except HTTPError as e:
        if e.response.status_code == 400:
            return None
        raise e

    set_tokens(request, oauth_client.access_token, oauth_client.refresh_token)

    return oauth_client


def _new_session(authorization_code=None, redirect_uri=None):
    temp_client = get()
    oauth = OAuth2Session(temp_client.client_id,
                          redirect_uri=redirect_uri,
                          scope=temp_client.scope)

    tokens = oauth.fetch_token(temp_client.token_url,
                               client_secret=temp_client.client_secret,
                               code=authorization_code,
                               verify=temp_client.verify)

    return get(access_token=tokens['access_token'],
               refresh_token=tokens['refresh_token'])
