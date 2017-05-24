# This Makefile consolidates and simplifies common operations on a
# Python project.

# Note: upload and release targets require configuration in .pypirc,
# like this:
## repository: http://pypi.23andme.io/jenkins/release/
## username: (user)
## password: (pass)

VERSION=$(shell python setup.py --version)

ifneq (,$(findstring dev,$(VERSION)))
	PYPI_INDEX=23dev
else
	PYPI_INDEX=23prd
endif

#=> default
default: tox

#=> setup
setup: develop

bdist bdist_egg bdist_wheel build develop install sdist: %:
	DJANGO_SETTINGS_MODULE='tests.config' python setup.py $@

#=> release -- build and upload package and docs
release:
	python setup.py register -r $(PYPI_INDEX) # idempotent -- okay if already registered
	python setup.py release -r $(PYPI_INDEX)

test: tox

tox:
	@tox

clean:
	@find . -name \*~ -exec rm -v '{}' +
	@find . -name \*.pyc -exec rm -v '{}' +
	@find . -name __pycache__ -prune -exec rm -vfr '{}' +
	@rm -fr build bdist cover dist sdist
	@rm -fr .tox .eggs
	@find . \( -name \*.orig -o -name \*.bak -o -name \*.rej \) -exec rm -v '{}' +
	@rm -fr distribute-* *.egg *.egg-info *.tar.gz nosetests.xml cover junit.xml coverage.xml .cache

.PHONY: default setup tox clean
