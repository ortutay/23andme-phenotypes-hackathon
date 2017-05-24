from . import client


def login_url(request):
    return {'login_url': client.login_url(request)}
