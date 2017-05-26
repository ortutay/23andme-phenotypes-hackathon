import pprint
import time

import requests

from my_app.my_app import utils
from my_app.my_app.models import Phenotype

pp = pprint.PrettyPrinter()


def do_request(accession_id, start, phenotype_id):
    r = {}
    counts = {}
    phenotypes = Phenotype.objects.filter(phenotype_id=phenotype_id)
    for phenotype in phenotypes:
        allele = utils.get_allele(phenotype.user.profile.ttam_token, accession_id, start, start + 1)
        print('%s -> %s' % (allele, phenotype.value))
        counts[allele] = counts.get(allele, 0) + 1
        r[allele] = r.get(allele, 0.0) + phenotype.value  # TODO: defauldict
    pp.pprint(r)
    for key in r.keys():
        r[key] /= counts[key]
    return r


def do_request_old(variant, pheno):
    pheno_query = 'AVG(%s)' % pheno
    body = """{
  "parameters": {
    "columns": [
      "%s", "%s", "count(1)"
    ],
    "from": "research_portal_consented",
    "group_by": ["%s"]
  }
}""" % (variant, pheno_query, variant)
    print(body)
    url = 'https://api.23andme.com/2/query/'
    headers = {
        'Authorization': 'Bearer 14b7591e0adbcd5aa63cb29b47a6388a',
        'Content-Type': 'application/json',
    }
    r = {}
    while True:
        resp = requests.post(url, headers=headers, data=body, verify=False)
        if resp.json()['status'] != 'Complete':
            time.sleep(1)
            continue
        for v in resp.json()['result']:
            variant_count = v[variant]
            if variant_count is None:
                continue
            r[variant_count] = v[pheno_query]
        break
    return r


if __name__ == '__main__':
    results = do_request('variant.NC_000016.9:53818459-53818460:T', 'composed_phenotype.weight')
    pp.pprint(results)
