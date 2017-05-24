from django.urls import reverse
from integration.specs.base import LiveTest

from my_app.lib.ttam_api.ttam_api.django.testing import authenticated, mock_ttam_api


class TestIndex(LiveTest):

    @authenticated()
    @mock_ttam_api()
    def test_index(self):
        self.driver.get(self.url(reverse('index')))
        assert 'Hello, world!' in self.driver.page_source
