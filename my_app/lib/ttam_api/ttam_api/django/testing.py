from unittest import mock
from my_app.lib.ttam_api.tests.fixtures.account import single_profile_account


ACCOUNT = single_profile_account['data'][0]


def _get_account_side_effect(account):
    def wrapper(api):
        account['owned_human_ids'] = set(human['id'] for human in account['profiles'])
        if account['profiles']:
            current_profile = account['profiles'][0]
        else:
            current_profile = None
        return account, current_profile
    return wrapper


def _unimplemented_side_effect(*args, **kwargs):
    return {'not implemented': 'no mock data to return'}


def authenticated(account=ACCOUNT):
    def real_decorator(func):
        def wrapper(*args, **kwargs):
            with mock.patch(
                    'my_app.lib.ttam_api.ttam_api.django.views._get_account',
                    side_effect=_get_account_side_effect(account)):
                return func(*args, **kwargs)
        return wrapper
    return real_decorator


def mock_ttam_api(delete=_unimplemented_side_effect,
                  get=_unimplemented_side_effect,
                  patch=_unimplemented_side_effect,
                  post=_unimplemented_side_effect,
                  put=_unimplemented_side_effect):
    def real_decorator(func):
        def wrapper(*args, **kwargs):
            with mock.patch('my_app.lib.ttam_api.ttam_api.django.views._get_api') as mock_api:
                mock_api.return_value = mock.MagicMock(**{
                    'delete.side_effect': delete,
                    'get.side_effect': get,
                    'patch.side_effect': patch,
                    'post.side_effect': post,
                    'put.side_effect': put
                })
                return func(*args, **kwargs)
        return wrapper
    return real_decorator
