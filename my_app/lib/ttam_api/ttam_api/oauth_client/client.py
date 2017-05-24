from six.moves.urllib.parse import urljoin
import funcy as fn
import json
import logging
import requests
import html2text

from cachecontrol import CacheControl

from django.http import StreamingHttpResponse

from oauthlib.oauth2 import WebApplicationClient  #, BackendApplicationClient
from requests_oauthlib import OAuth2Session

from ..exceptions import (
    UnauthenticatedException,
    PermissionDenied,
    APIError,
    NotFound,
    BadRequest,
    Unprocessable,
)

log = logging.getLogger(__name__)


class OauthClient(object):

    def __init__(self,
                 access_token=None,
                 refresh_token=None,
                 client_id=None,
                 client_secret=None,
                 scope=None,
                 api_url=None,
                 redirect_url=None,
                 verify=False,
                 debug=False,
                 ):

        self.access_token = access_token
        self.refresh_token = refresh_token
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope
        self.api_url = api_url
        self.redirect_url = redirect_url
        self.verify = verify
        self.debug = debug
        self.token_url = self.make_url('/token/')

    def make_url(self, resource):
        return urljoin(self.api_url, resource)

    def get_token(self, authorization_code):
        return self.client.fetch_token(self.token_url,
                                       client_secret=self.client_secret,
                                       code=authorization_code,
                                       verify=self.verify)

    def get(self, resource, **kwargs):
        url = self.make_url(resource)
        params = kwargs.pop('params', {})

        client = self.client
        retry_get = fn.retry(2, errors=requests.ConnectionError)(client.get)
        response = retry_get(url, params=params, verify=self.verify, **kwargs)

        self._handle_errors(response)

        data = self._get_json(response)

        self._log(url, data, params)

        return data

    def post(self, resource, **kwargs):
        client = self.client
        if kwargs.get('files', None) is None:
            return self._non_idempotent_send(resource, client.post, **kwargs)
        else:
            # files and json cannot be sent together, but files and data can
            json = kwargs.pop('json', None)
            return self._non_idempotent_send(resource, client.post, data=json, **kwargs)

    def delete(self, resource, **kwargs):
        client = self.client
        return self._non_idempotent_send(resource, client.delete, **kwargs)

    def patch(self, resource, **kwargs):
        client = self.client
        return self._non_idempotent_send(resource, client.patch, **kwargs)

    def put(self, resource, **kwargs):
        client = self.client
        return self._non_idempotent_send(resource, client.put, **kwargs)

    def _non_idempotent_send(self, resource, method, **kwargs):
        url = self.make_url(resource)

        response = method(url, verify=self.verify, **kwargs)
        self._handle_errors(response)

        data = self._get_json(response)
        self._log(url, data)
        return data

    @fn.cached_property
    def base_client(self):
        return WebApplicationClient(self.client_id,
                                    access_token=self.access_token,
                                    refresh_token=self.refresh_token)

    @fn.cached_property
    def client(self):
        token = {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
        }
        return CacheControl(
            OAuth2Session(client=self.base_client,
                          token=token,
                          redirect_uri=self.redirect_url,
                          )
        )

    def _get_json(self, response):
        try:
            return response.json()
        except Exception:
            log.exception('url: %s\ncontent:\n%s', response.url, response.content, exc_info=True)
            raise

    def _decode_if_json(self, response):
        """
        Decode a JSON response, or the raw response if it's not JSON
        """
        try:
            return self._get_json(response)
        except ValueError:
            return response.content

    def _handle_errors(self, response):
        code = response.status_code
        if code == 400:
            raise BadRequest(self._decode_if_json(response))
        if code == 401:
            raise UnauthenticatedException(self._decode_if_json(response))
        if code == 403:
            raise PermissionDenied(self._decode_if_json(response))
        if code == 404:
            raise NotFound(self._decode_if_json(response))
        if code == 422:
            raise Unprocessable(self._decode_if_json(response))
        if code == 500:
            if self.debug:
                self._log_error(response)
            raise APIError()

    def _log_error(self, response):
            log.error(
                '\n\n -- API ERROR --\n%s: %s\n%s %s\n\n%s' % (
                    response.status_code, response.reason, response.request.method,
                    response.url, html2text.html2text(response.text)
                )
            )
            raise APIError(response.reason)

    def _log(self, url, data, params=None):
        st = 'URL: %s\n Params: %s\n Response: %s' % (url, params, json.dumps(data, indent=2))
        log.debug(st)

    def download(self, resource, filename=None, chunk_size=4096):
        """Relay a streaming response from the API to a file download."""
        url = self.make_url(resource)
        api_response = self.client.get(url, verify=self.verify)

        self._handle_errors(api_response)
        file_response = StreamingHttpResponse(api_response.iter_content(chunk_size=chunk_size),
                                              content_type=api_response.headers['content-type'])
        if filename:
            file_response['Content-Disposition'] = 'attachment; filename="%s"' % filename
        elif 'Content-Disposition' in api_response.headers:
            file_response['Content-Disposition'] = api_response.headers['Content-Disposition']
        else:
            file_response['Content-Disposition'] = 'attachment'

        try:
            file_response['Content-Length'] = api_response.headers['Content-Length']
        except KeyError:
            pass  # leave them guessing

        return file_response
