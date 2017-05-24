import os

from django.contrib.staticfiles.testing import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver

BROWSERSTACK_USER = os.environ.get('BROWSERSTACK_USER', '')
BROWSERSTACK_KEY = os.environ.get('BROWSERSTACK_KEY', '')
BROWSERSTACK_URL = 'http://{}:{}@hub.browserstack.com/wd/hub'.format(BROWSERSTACK_USER, BROWSERSTACK_KEY)
HEADLESS = os.environ.get('INTEGRATION_HEADLESS', 'false').lower() == 'true'
HEADLESS_URL = os.environ.get('INTEGRATION_HEADLESS_URL', BROWSERSTACK_URL)
HEADLESS_IDENTIFIER = os.environ.get('BITBUCKET_COMMIT', '')
GIT_BRANCH = os.environ.get('BITBUCKET_BRANCH', '')
BROWSERSTACK_BUILD = os.environ.get('BITBUCKET_COMMIT', '')
build = '{} {}'.format(GIT_BRANCH, BROWSERSTACK_BUILD).replace('/', '_').replace('-', '_')
desired_capabilities = {
    'project': 'my_app',
    'build': build,
    'acceptSslCerts': True,
    'browserstack.local': True,
    'browserstack.localIdentifier': HEADLESS_IDENTIFIER,
    'browser': 'Chrome',
    'os': 'OS X',
    'os_version': 'Sierra',
    'resolution': '1024x768',
}


class LiveTest(LiveServerTestCase):
    def setUp(self):
        super().setUp()
        if HEADLESS:
            name = '{}_{}_{}_{}'.format(
                self.id(), desired_capabilities['browser'],
                desired_capabilities['os'], desired_capabilities['os_version'])
            cap = desired_capabilities.copy()
            cap['name'] = name
            self.driver = webdriver.Remote(
                command_executor=HEADLESS_URL,
                desired_capabilities=cap)
        else:
            self.driver = WebDriver()

    def tearDown(self):
        self.driver.quit()
        super().tearDown()

    def url(self, path='/'):
        """ Takes a path and adds the live server URL to it. Easypeasy """
        return '%s%s' % (self.live_server_url, path)
