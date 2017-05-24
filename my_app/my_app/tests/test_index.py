from django.test import TestCase
from django.urls import reverse

from my_app.my_app.fixtures.account import art_vandalay
from my_app.lib.ttam_api.ttam_api.django.testing import authenticated, mock_ttam_api


ACCESSION_LENGTH = 191154276


def get_side_effect(resource, params={}, data={}):
    if '3/accession' in resource:
        return {
            'id': 'NC_000004.11',
            'chromosome': 4,
            'length': ACCESSION_LENGTH
        }
    else:
        return {'data': None}


class TestIndex(TestCase):
    url = reverse('index')

    @authenticated()
    @mock_ttam_api(get=get_side_effect)
    def test_hello_world(self):
        resp = self.client.get(self.url, follow=True)
        assert resp.status_code == 200
        content = str(resp.content)

        assert 'Hello, world!' in content
        assert str(ACCESSION_LENGTH) in content

    @authenticated(account=art_vandalay)
    @mock_ttam_api()
    def test_ttam_account_name(self):
        resp = self.client.get(self.url, follow=True)
        assert resp.status_code == 200
        assert art_vandalay['first_name'] in str(resp.content)
