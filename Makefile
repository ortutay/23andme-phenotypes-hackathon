MAKEFLAGS?=-j4
ifeq ($(shell uname -s),Darwin)
	LDFLAGS = "-I/usr/local/opt/openssl/include -L/usr/local/opt/openssl/lib"
endif

all:
ifndef VIRTUAL_ENV
	@echo "You need make and activate a virtualenv first:"
	@echo "make venv"
	@echo "source venv/bin/activate"
	@exit
else
	@$(MAKE) build
endif

build: pip npm
	@./manage.py collectstatic --no-input --clear
	@$(MAKE) migrate
	@$(MAKE) init_db

init_db:
	@./manage.py loaddata my_app/my_app/fixtures/initial_data.json

migrate:
	@./manage.py migrate

pip:
	@pip install --force-reinstall pip==9.0.1
	@LDFLAGS=$(LDFLAGS) pip install -r requirements/local.txt

npm:
	@npm install
	@npm run build

start: migrate
	@PYTHONUNBUFFERED=1 honcho start -f Procfile.dev

venv:
	@virtualenv --python=python3.6 venv

test:
	@npm run lint:js
	@npm run lint:scss
	@pytest my_app --cov-report term-missing --cov=my_app --ignore=my_app/lib
	@pytest integration --rerun 3
	@DATABASE_URL='sqlite:///dev.sqlite' DJANGO_DEBUG=False DJANGO_SECRET_KEY='%c$z9@gf)58ewo3_8@q#2)a8xot-5oe5+n7r*z21x69(g#p^)3dgw' DJANGO_SETTINGS_MODULE=config.settings.production ./manage.py check --deploy

clean:
	@rm -rf venv
	@rm -rf node_modules
	@rm -rf my_app/assets/public/js/*.js*
	@rm -rf my_app/assets/public/css/*.css*
	@rm -rf static
	@find . -name \*.pyc -delete
	@find . -name __pycache__ -delete

.PHONY: all start venv test clean integration
