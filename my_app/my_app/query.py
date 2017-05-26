import pprint
import time

import requests

pp = pprint.PrettyPrinter()


def do_request(variant, pheno):
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
