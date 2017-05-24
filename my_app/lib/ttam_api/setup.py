from setuptools import setup, find_packages

import re
import subprocess


def _get_version_from_git_tag():
    """Return a PEP440-compliant version derived from the git status.
    If that fails for any reason, return the first 7 chars of the changeset hash.
    """

    def _is_dirty():
        try:
            subprocess.check_call(['git', 'diff', '--quiet'])
            subprocess.check_call(['git', 'diff', '--cached', '--quiet'])
            return False
        except subprocess.CalledProcessError:
            return True

    def _get_most_recent_tag():
        most_recent = subprocess.check_output(["git", "describe", "--tags"]).strip()
        return most_recent.decode('utf-8')

    def _get_hash():
        return subprocess.check_output(["git", "rev-parse", "HEAD"]).strip()[:7]

    tag = _get_most_recent_tag()
    m = re.match("(?P<xyz>\d+\.\d+\.\d+)(?:-(?P<dev>\d+)-(?P<hash>.+))?", tag)


    version = m.group('xyz')
    if m.group('dev') or _is_dirty():
        version += ".dev{dev}+{hash}".format(dev=m.group('dev') or 0,
                                             hash=m.group('hash') or _get_hash())

    return version

# Most config should happen here:
name = slug = 'ttam.api'
# version = _get_version_from_git_tag()
description = "one-liner description"
long_description = """
A longer description of your awesome package.
"""
package_data = {name: ['_/*/*']}

setup(
    author='23andMe Engineering',
    author_email='eng@23andme.com',
    description=description,
    license='23andMe Proprietary',
    long_description=long_description,
    name=name,
    namespace_packages=['ttam'],
    package_data=package_data,
    packages=find_packages(),
    url='https://bitbucket.org/23andme/' + slug,
    # version=version,
    zip_safe=True,

    install_requires=[
        'CacheControl>=0.11.5',
        'funcy>=1.6',
        'oauthlib>=1.0.3',
        'requests-oauthlib>=0.5.0',
        'requests>=2.7.0',
        'six>=1.10.0',
        'html2text==2016.9.19'
    ],
    setup_requires=['pytest-runner'],
    tests_require=[
        'Django>=1.8.7',
        'django-debug-toolbar>=1.4.0',
        'mock',
        'pytest-cov',
        'pytest-django>=2.9.1',
        'pytest',
        'python-dateutil>=2.4.2',
        'six>=1.10.0',
        'tox',
        'html2text==2016.9.19'
    ],
)
