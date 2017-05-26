import requests
from my_app.my_app import utils


def process(token):
    d = {}
    d['fitbit_avg_num_steps'] = get_avg_steps(token)
    d['fitbit_avg_heartrate'] = get_resting_heartrate(token)
    d['fitbit_sleep_duration'] = get_sleep_duration(token)
    return d


def get_sleep_duration(token):
    url = 'https://api.fitbit.com/1.2/user/-/sleep/list.json?beforeDate=2017-03-27&sort=desc&offset=0&limit=1'
    auth_header = "Bearer " + token
    headers = {"Authorization": auth_header}
    r = requests.get(url, headers=headers)
    d = r.json()
    v = 0.
    for i in d['sleep']:
        v += int(i['minutesAsleep'])
    v = v/len(d['sleep'])
    return v


def get_resting_heartrate(token):
    url = 'https://api.fitbit.com/1/user/-/activities/heart/date/today/30d.json'
    auth_header = "Bearer " + token
    headers = {"Authorization": auth_header}
    r = requests.get(url, headers=headers)
    d = r.json()
    v = 0.
    count = 0
    for i in d['activities-heart']:
        if 'restingHeartRate' not in i['value']:
            continue
        count += 1
        v += int(i['value']['restingHeartRate'])
    v = v/count
    return v


def get_avg_steps(token):
    url = 'https://api.fitbit.com/1/user/-/activities/steps/date/today/1y.json'
    auth_header = "Bearer " + token
    headers = {"Authorization": auth_header}
    r = requests.get(url, headers=headers)
    d = r.json()
    total_steps = 0.
    for i in d['activities-steps']:
        total_steps += int(i['value'])
    avg_steps = total_steps/len(d['activities-steps'])
    return avg_steps


if __name__ == '__main__':
    ttam_token = '958627908df486c076dcf9e2fe15d350'
    utils.get_genotype_id(ttam_token)
    d = process('eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI1Skw0RDciLCJhdWQiOiIyMjhKRjciLCJpc3MiOiJGaXRiaXQiLCJ0eXAiOiJhY2Nlc3NfdG9rZW4iLCJzY29wZXMiOiJyc29jIHJzZXQgcmFjdCBybG9jIHJ3ZWkgcmhyIHJwcm8gcm51dCByc2xlIiwiZXhwIjoxNDk1Nzg3NzM2LCJpYXQiOjE0OTU3NTg5MzZ9.97eAWOUqdxK5ZE3zdk3-vI2tcZ1bTKPKr7ypmt-oUQQ')
    utils.to_hbase_insert(ttam_token, d)
