from functools import wraps
import json
import requests

def map_auth_response_key(resp, platform):
    user_info = {}
    
    if not platform:
        raise ValueError('incorrect platform parameter')
    elif platform == 'twitter':
        user_info = resp
    elif platform == 'kakao':
        with requests.Session() as session:
            session.headers.update({
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': f'Bearer {resp["access_token"]}'
            })
            response = session.post('https://kapi.kakao.com/v2/user/me')

        response_data = json.loads(response.content)
        user_info['user_id'] = response_data.get('id')
        user_info['screen_name'] = response_data.get('kakao_account').get('profile').get('nickname')
        user_info['oauth_token'] = resp['access_token']
        user_info['oauth_token_secret'] = ''

    print(f'user_info: {user_info}')
    return user_info
