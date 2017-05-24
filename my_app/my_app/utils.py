import json
import requests

# Config stuff, should move this at some point

TTAM_API_SERVER = 'https://api.23andme.product'


def to_url(path):
    return '%s%s' % (TTAM_API_SERVER, path)


def headers(ttam_token):
    return {'Authorization': 'Bearer %s' % ttam_token}


def get_profile_id(ttam_token):
    url = to_url('/3/account/')
    resp = requests.get(url, verify=False, headers=headers(ttam_token))
    return json.loads(resp.content)['data'][0]['profiles'][0]['id']


def get_phenotype(ttam_token, phenotype_id):
    profile_id = get_profile_id(ttam_token)
    url = to_url('/3/profile/%s/phenotype/?id=%s' % (profile_id, phenotype_id))
    resp = requests.get(url, verify=False, headers=headers(ttam_token))
    return json.loads(resp.content)['data'][0]['value']


def write_phenotype(ttam_token, phenotype_id, value):
    profile_id = get_profile_id(ttam_token)
    data = {}
    data[phenotype_id] = value
    url = to_url('/3/profile/%s/phenotype/' % profile_id)
    resp = requests.post(url, verify=False, data=data, headers=headers(ttam_token))
    print resp


if __name__ == '__main__':
    token = '61f377b4d485771c3dfdf848b38322e6'
    write_phenotype(token, 'weight_g', 300)
    print get_phenotype(token, 'weight_g')
