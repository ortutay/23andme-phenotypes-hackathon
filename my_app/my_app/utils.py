import json
import requests

# Config stuff, should move this at some point

TTAM_API_SERVER = 'https://api.23andme.product'


def to_url(path):
    return '%s%s' % (TTAM_API_SERVER, path)


def headers(ttam_token):
    return {'Authorization': 'Bearer %s' % ttam_token}


def get_genotype_id(ttam_token):
    url = to_url('/3/account/')
    resp = requests.get(url, verify=False, headers=headers(ttam_token))
    print(resp.json())
    # return resp.json()['data'][0]['profiles'][0]['id']


def get_profile_id(ttam_token):
    url = to_url('/3/account/')
    resp = requests.get(url, verify=False, headers=headers(ttam_token))
    print(resp.json())
    return resp.json()['data'][0]['profiles'][0]['id']


def get_phenotypes(ttam_token, phenotype_ids):
    print('ttam_token', ttam_token)
    profile_id = get_profile_id(ttam_token)
    url = to_url('/3/profile/%s/phenotype/?id=%s' % (profile_id, ','.join(phenotype_ids)))
    resp = requests.get(url, verify=False, headers=headers(ttam_token))
    print('got resp')
    print(resp.json())
    return {x['id']: x['value'] for x in resp.json()['data']}


def set_phenotype(ttam_token, phenotype_id, value):
    profile_id = get_profile_id(ttam_token)
    data = {}
    data[phenotype_id] = value
    url = to_url('/3/profile/%s/phenotype/' % profile_id)
    requests.post(url, verify=False, data=data, headers=headers(ttam_token))


def to_hbase_insert(ttam_token, phenotypes):
    for id, val in phenotypes.items():
        print("""UPSERT INTO ibd_pheno (concept_id, concept_name, genotype_id, float_val) VALUES ('%s', '%s', %s, %s);""" % (id, id, 123, val))


if __name__ == '__main__':
    token = 'TODO'
    set_phenotype(token, 'fitbit_num_steps', 90)
    print(get_phenotypes(token, ['fitbit_num_steps']))
