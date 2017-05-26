import arrow
import os
import pprint
import requests

from watson_developer_cloud import PersonalityInsightsV3, VisualRecognitionV3

pp = pprint.PrettyPrinter()

from joblib import Memory
CACHE_DIR = '/tmp/ttam-hack-cache'
os.makedirs(CACHE_DIR, exist_ok=True)
memory = Memory(cachedir=CACHE_DIR)


CREDENTIALS_PERSONALITY = {
    'url': 'https://gateway.watsonplatform.net/personality-insights/api',
    'username': '94fe352e-21e4-4707-8833-b2df47fb6f6f',
    'password': 'uLtJGyuy6JXJ'
}

CREDENTIALS_VISUAL = {
    "url": "https://gateway-a.watsonplatform.net/visual-recognition/api",
    "note": "It may take up to 5 minutes for this key to become active",
    "api_key": "33fd2c569c07286c0deb887c58d80c61e514634d"
}

personality_insights = PersonalityInsightsV3(
    version='2016-10-20',
    username=CREDENTIALS_PERSONALITY['username'],
    password=CREDENTIALS_PERSONALITY['password'])


visual_recognition = VisualRecognitionV3(
    '2016-05-20',
    api_key=CREDENTIALS_VISUAL['api_key'])


@memory.cache
def process(access_token):
    # return {'facebook_images_avg_people': 1.24}
    phenos = {}
    for k, v in process_posts(access_token).items():
        phenos[k] = v
    for k, v in process_images(access_token).items():
        phenos[k] = v
    return phenos


def process_posts(access_token):
    resp = requests.get('https://graph.facebook.com/v2.9/me/posts?access_token=%s&limit=1000' % access_token)
    posts = resp.json()['data']
    watson_posts = []

    for post in posts:
        if 'message' not in post:
            continue
        watson_posts.append({
            'content': post['message'],
            'contenttype': 'text/plain',
            'id': post['id'],
            'language': 'en',
            'created': arrow.get(post['created_time']).timestamp,
        })

    watson_posts.append({
        'content': 'abc ' * 100,
        'contenttype': 'text/plain',
        'id': post['id'],
        'language': 'en',
        'created': arrow.get().timestamp,
    })

    score = personality_insights.profile(
        {'contentItems': watson_posts},
        content_type='application/json',
        raw_scores=True,
        consumption_preferences=True)
    phenos = {'facebook_posts_personality_%s' % x['name'].lower(): x['percentile'] for x in score['personality']}
    return phenos


def process_images(access_token):
    resp = requests.get('https://graph.facebook.com/v2.9/me/photos?access_token=%s&fields=picture.type(large)' % access_token)
    images = resp.json()['data']
    count = 0.
    for image in images[:5]:
        resp = visual_recognition.detect_faces(images_url=image['picture'])
        count += len(resp['images'][0]['faces'])
    phenos = {
        'facebook_images_avg_people': count / len(images),
    }
    return phenos


if __name__ == '__main__':
    r = process('EAAH8H7ZAoUBIBALWoQxmtlFYHLadgLAerBGYJp86ZAY6jnvl2hwUZAxt2CqktpfWSMKGfHTYS8K1DtZAThJ5TFr1aJt1W20W32ux9mPHOhlo1RdIbXSyZCYK2OdfJcG3Of2PbBY1ZC1Tn0OSANQiPgoicCiqJfTQyZAqpjbTRVJ9VFnWhkuZAWuzA9ZAcknk8Wp8ZD')
    pp.pprint(r)
