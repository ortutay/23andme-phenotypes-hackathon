from django.urls import reverse

from integration.specs.base import LiveTest


class StatusTest(LiveTest):

    def test_status(self):
        """ Tests the _status endpoint for deployments """
        self.driver.get(self.url(reverse('status')))
        assert 'Status: OK' in self.driver.page_source
