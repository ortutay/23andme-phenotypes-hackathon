import os
import json
import requests

from my_app.my_app.models import Phenotype

from joblib import Memory
CACHE_DIR = '/tmp/ttam-hack-cache'
os.makedirs(CACHE_DIR, exist_ok=True)
memory = Memory(cachedir=CACHE_DIR)

TTAM_API_SERVER = 'https://api.23andme.com'


def to_url(path):
    return '%s%s' % (TTAM_API_SERVER, path)


def headers(ttam_token):
    return {'Authorization': 'Bearer %s' % ttam_token}


@memory.cache
def get_variant_from_marker(marker_id):
    url = to_url('/3/marker/%s/' % marker_id)
    resp = requests.get(url, verify=False)
    d = resp.json()
    return d['accession_id'], d['start']


@memory.cache
def get_profile_id(ttam_token):
    url = to_url('/3/account/')
    resp = requests.get(url, verify=False, headers=headers(ttam_token))
    print(resp)
    print(resp.json())
    return resp.json()['data'][0]['profiles'][0]['id']


def get_allele(ttam_token, accession_id, start, end):
    profile_id = get_profile_id(ttam_token)
    url = to_url('/3/profile/%s/variant/?accession_id=%s&start=%s&end=%s' % (profile_id, accession_id, start, end))
    print(url)
    resp = requests.get(url, verify=False, headers=headers(ttam_token))
    print('ALLELES')
    print(resp.json())
    d = resp.json()
    alleles = []
    for v in d['data']:
        for i in range(int(v['dosage'])):
            alleles.append(v['allele'])
    alleles.sort()
    return ''.join(alleles)


def get_phenotypes(ttam_token, phenotype_ids):
    profile_id = get_profile_id(ttam_token)
    # import pdb; pdb.set_trace()
    phenotypes = Phenotype.objects.filter(
        profile_id=profile_id,
        phenotype_id__in=phenotype_ids)
    print('phenotypes', phenotypes)
    return {p.phenotype_id: p.value for p in phenotypes}


def set_phenotype(user, phenotype_id, value):
    profile_id = get_profile_id(user.profile.ttam_token)
    if Phenotype.objects.filter(profile_id=profile_id, phenotype_id=phenotype_id).exists():
        return
    Phenotype(
        user=user,
        profile_id=profile_id,
        phenotype_id=phenotype_id,
        value=value).save()


def get_phenotypes_old(ttam_token, phenotype_ids):
    print('ttam_token', ttam_token)
    profile_id = get_profile_id(ttam_token)
    url = to_url('/3/profile/%s/phenotype/?id=%s' % (profile_id, ','.join(phenotype_ids)))
    resp = requests.get(url, verify=False, headers=headers(ttam_token))
    print('got resp')
    print(resp.json())
    return {x['id']: x['value'] for x in resp.json()['data']}


def set_phenotype_old(ttam_token, phenotype_id, value):
    profile_id = get_profile_id(ttam_token)
    data = {}
    data[phenotype_id] = value
    url = to_url('/3/profile/%s/phenotype/' % profile_id)
    requests.post(url, verify=False, data=data, headers=headers(ttam_token))


if __name__ == '__main__':
    print(get_variant_from_marker('rs1558902'))
    # token = '4c210fc3755b298a2d84bbacf2b0d4ab'
    # print(get_variant(token, 'NC_000016.9', 53803574, 53803575))
    # set_phenotype(token, 'fitbit_num_steps', 90)
    # print(get_phenotypes(token, ['fitbit_num_steps']))
