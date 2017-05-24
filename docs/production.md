Production Environment
======================

This document contains information on how to set up a production instance of this application. It's split into two parts: one for general production setup that applies to all deployment platforms and one for additional Heroku specific configuration.

General Configuration
---------------------
### Environment Variables
This app has several environment variables that it needs to run.

- `DATABASE_URL`
    - Heroku sets this for you when you have a DB add-on.
- `DEBUG`
    - Set to 'false' to disable debug tools and optimize for production.
- `DJANGO_SECRET_KEY`
    - Very important. Use a random hash from a reliable source of randomness. So it's like, totally random.
- `DJANGO_SETTINGS_MODULE`: config.settings.production
    - So that Heroku knows which settings file to default to
- `API_CLIENT_ID`
    - Public oauth client id, super important to authenticate against the 23andme API
- `API_CLIENT_SECRET`
    - Secret oauth client hash for API authentication
- `API_URL`
    - The 23andme api url, default is 'https://api.23andme.com'

### Configuration

#### Gunicorn
Gunicorn is used instead of the built in Django server. It has several options that need to be changed for performance. These options are set on the commandline when invoking Gunicorn. Check out these [docs](http://docs.gunicorn.org/en/18.0/configure.html) for more information. Gunicorn also takes care of serving static files through DJ Static.

#### Django production optimizations
All production Django optimization settings can be found in the `settings/production.py` file. This settings file is used when the application is started with `wsgi.py`, like with Gunicorn.

Heroku
------
Using Heroku to serve this application is a quick way to get it running and is free until you want to get serious. Heroku's [tutorial](https://devcenter.heroku.com/articles/getting-started-with-django) should cover the basics, and can be roughly summarized:

1. [Sign up](ihttps://signup.heroku.com/) for an account.
1. You'll want to make sure you have the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) tool with `brew install heroku`
1. Sign in with `heroku login`
1. Create your app in heroku with `heroku create`
1. You can add the environemnt [variables](https://devcenter.heroku.com/articles/config-vars) above with `heroku config:set VAR=val`
1. Deploy your code with `git push heroku master`

Generally, you'll want to keep the master branch of your repo in sync with your heroku deployment.

At this point, you'll probably hit some errors because you still need to configure a node.js buildpack - have no fear, keep reading!

### Buildpacks
Buildpacks are pre-set language-specific pipelines that run every time a server is fired up with your code and makes sure it will translate into something that can be executed. Heroku should detect that this is a Python app and use the Python buildpack to run a standard Django build.

But this app also uses Grunt for the asset pipeline, so Heroku needs a node.js buildpack too. It's important to run this buildpack before the Python one so Grunt can compile assets before Django runs collectsatic. Adding it is as simple as `heroku buildpacks:add --index 1 heroku/nodejs`. `--index=1` ensures that this is the first buildpack in the list.

Now Heroku will initialize a node.js environment and read the `package.json` to install npm dependencies and run the `postinstall` directive (which is set to simply run `grunt`) before even thinking about Python on every deoployment. For more information, check out this [artical](https://devcenter.heroku.com/articles/using-multiple-buildpacks-for-an-app). Also, for some reason, the Python buildpack was not running collectstatic, so a custom `bin/post_compile` is configured to run it after the standard buildpacks finish.

### Add-ons
Heroku allows you to attach Add-ons to your app, usually for a price. This app only needs one to start, and Heroku should automatically detect/attach it:

- Postgres
    - `hobby-dev`: Free and allows for 20 connections and more than enough storage while you're still developing. Once you get serious, you'll probably want to open up your wallet and bump it up to `standard-0` for 60 connections and more storage than you'll know what to do with.

### Dynos
A dyno is Heroku's server abstraction. 1 dyno is like 1 server. Heroku allows you to run an application on 1 dyno for free. This is great for testing, but Heroku will periodically put 1 dyno app to sleep (causing a slow initial page load) as detailed in this [blog post](https://blog.heroku.com/archives/2013/6/20/app_sleeping_on_heroku). For production you'll want to use at least 2 dynos so this doesn't happen.

