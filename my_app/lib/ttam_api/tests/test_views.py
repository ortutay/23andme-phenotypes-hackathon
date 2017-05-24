import mock

from django.contrib.sessions.middleware import SessionMiddleware
from django.http import JsonResponse
from django.test import TestCase, RequestFactory
from django.views.generic import View

from my_app.lib.ttam_api.ttam_api.django.views import OauthCallbackView, AuthenticatedMixin
from my_app.lib.ttam_api.ttam_api.django.client import login_url
from my_app.lib.ttam_api.ttam_api.django import client


TEMP_TIMEOUT = 60


class TestOauthCallbackView(TestCase):

    def setUp(self):
        self.rf = RequestFactory()

    def test_no_code(self):
        req = self.rf.get('/oauth_callback/')
        res = OauthCallbackView.as_view()(req)
        self.assertRedirects(res, login_url(req), fetch_redirect_response=False)

    @mock.patch.object(client, 'authenticate')
    def test_good_code(self, mock_client_authenticate):
        mock_client_authenticate.return_value = 'good'

        req = self.rf.get('/oauth_callback/', {'code': 'good_code'})
        req.session = mock.MagicMock()
        res = OauthCallbackView.as_view()(req)
        assert res.status_code == 302
        assert res['Location'] == '/'

    @mock.patch.object(client, 'authenticate')
    def test_good_code_with_redirect(self, mock_client_authenticate):
        mock_client_authenticate.return_value = 'good'

        req = self.rf.get(
            '/oauth_callback/',
            {'code': 'good_code', 'state': '{"origin_uri": "/reports/"}'})
        req.session = mock.MagicMock()
        res = OauthCallbackView.as_view()(req)
        assert res.status_code == 302
        assert res['Location'] == '/reports/'

    @mock.patch.object(client, 'authenticate')
    def test_good_code_with_bogus_redirect(self, mock_client_authenticate):
        mock_client_authenticate.return_value = 'good'

        req = self.rf.get(
            '/oauth_callback/',
            {'code': 'good_code', 'state': '{"origin_uri": "https://google.com/"}'})
        req.session = mock.MagicMock()
        with self.assertRaises(ValueError):
            OauthCallbackView.as_view()(req)

    @mock.patch.object(client, 'authenticate')
    def test_good_code_with_sneaky_bogus_redirect(self, mock_client_authenticate):
        mock_client_authenticate.return_value = 'good'

        req = self.rf.get(
            '/oauth_callback/',
            {'code': 'good_code', 'state': '{"origin_uri": "//google.com/"}'})
        req.session = mock.MagicMock()
        with self.assertRaises(ValueError):
            OauthCallbackView.as_view()(req)


class AuthView(AuthenticatedMixin, View):

    """ View to test auth mixin """

    def get(self, *args, **kwargs):
        return JsonResponse({'error': 'Can\'t cache this. Hammer time.'})


class TestAuthenticatedMixin(TestCase):

    def setUp(self):
        self.rf = RequestFactory()

    def tearDown(self):
        del self.rf

    def test_no_api_redirect(self):
        """ Make sure authenticated views redirect if api is None """
        req = self.rf.get('/')
        req.api = None
        SessionMiddleware().process_request(req)
        req.session.save()
        res = AuthView.as_view()(req)
        assert res.status_code == 302
        assert res['Location'] == login_url(req)

    def test_ajax_401_no_api(self):
        req = self.rf.get('/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        req.api = None
        SessionMiddleware().process_request(req)
        req.session.save()
        res = AuthView.as_view()(req)
        assert res.status_code == 401
