import json
import mock

from django.http import JsonResponse, HttpResponseRedirect
from django.test import TestCase, RequestFactory
from django.views.generic import View
from django.contrib.sessions.middleware import SessionMiddleware

from my_app.lib.ttam_api.ttam_api.django.views import AuthenticatedMixin
from my_app.lib.ttam_api.ttam_api.django import client
from my_app.lib.ttam_api.tests.fixtures.account import multiprofile_account, single_profile_account


class AuthView(AuthenticatedMixin, View):

    """view to test auth mixin"""

    def get(self, request):
        api = getattr(request.ttam, 'api', None)
        data = {
            'current_profile': getattr(request.ttam, 'current_profile', None),
            'has_ttam_api': api is not None
        }
        return JsonResponse(data)


class TestAuthenticatedMixinDispatch(TestCase):

    accounts_response = single_profile_account
    multi_profile_accounts_response = multiprofile_account

    def setUp(self):
        self.req = RequestFactory().get('/')
        SessionMiddleware().process_request(self.req)
        self.req.session.save()
        self.view = AuthView()

    @mock.patch.object(client, 'get')
    def _get_response(self, mock_client_get):
        mock_client_get.return_value = mock.MagicMock(**{'get.return_value': self.accounts_response})

        return self.view.dispatch(self.req)

    @mock.patch.object(client, 'get')
    def _get_multi_profile_response_data(self, mock_client_get):
        mock_client_get.return_value = mock.MagicMock(**{'get.return_value': self.multi_profile_accounts_response})

        res = self.view.dispatch(self.req)
        return json.loads(res.content.decode('utf-8'))

    def _get_response_data(self):
        res = self._get_response()
        return json.loads(res.content.decode('utf-8'))

    @mock.patch.object(client, 'get_tokens')
    def test_attaches_profile(self, mock_client_get_tokens):
        mock_client_get_tokens.return_value = ('access_token', 'refresh_token')

        data = self._get_response_data()
        expected_profile = self.accounts_response['data'][0]['profiles'][0]
        assert data['current_profile'] == expected_profile

    @mock.patch.object(client, 'get_tokens')
    def test_attaches_fisrt_profile_for_multiprofile_account(self, mock_client_get_tokens):
        mock_client_get_tokens.return_value = ('access_token', 'refresh_token')

        data = self._get_multi_profile_response_data()
        expected_profile = self.multi_profile_accounts_response['data'][0]['profiles'][0]
        assert data['current_profile'] == expected_profile

    @mock.patch.object(client, 'get_tokens')
    def test_attaches_ttam_api(self, mock_client_get_tokens):
        mock_client_get_tokens.return_value = ('access_token', 'refresh_token')

        data = self._get_response_data()
        assert data['has_ttam_api']

    @mock.patch.object(client, 'get_tokens')
    def test_redirects_if_no_access_token(self, mock_client_get_tokens):
        mock_client_get_tokens.return_value = (None, 'refresh_token')

        res = self._get_response()
        assert res.status_code == 302
        assert isinstance(res, HttpResponseRedirect)

    @mock.patch.object(client, 'get_tokens')
    def test_redirects_if_no_refresh_token(self, mock_client_get_tokens):
        mock_client_get_tokens.return_value = ('access_token', None)

        res = self._get_response()
        assert res.status_code == 302
        assert isinstance(res, HttpResponseRedirect)
