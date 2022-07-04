from datetime import datetime
from flask import Flask, request, redirect, url_for, session, flash, g, render_template
from flask_oauthlib.client import OAuth
from models.model import User, db_session
from lib import common

app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')

oauth = OAuth()
twitter = oauth.remote_app(
    'twitter',
    base_url='https://api.twitter.com/1.1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    authorize_url='https://api.twitter.com/oauth/authorize',
    access_token_url='https://api.twitter.com/oauth/access_token',
    consumer_key=app.config.get('TWITTER_CONSUMER_KEY'),
    consumer_secret=app.config.get('TWITTER_CONSUMER_SECRET')
)

kakao = oauth.remote_app(
    'kakao',
    base_url='https://kapi.kakao.com/v2/',
    authorize_url='https://kauth.kakao.com/oauth/authorize',
    access_token_url='https://kauth.kakao.com/oauth/token',
    consumer_key=app.config.get('KAKAO_CONSUMER_KEY'),
    consumer_secret=app.config.get('KAKAO_CONSUMER_SECRET')
)

@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = db_session.query(User).filter_by(user_id=session['user_id']).first()

@app.after_request
def after_request(response):
    db_session.close()
    # response.headers["Pragma"] = "no-cache"
    # response.headers["Expires"] = "0"
    # response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    # response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    print(f'response status_code: {response.status_code}')

    return response

@twitter.tokengetter
def get_twitter_token():
    user = g.user
    if user is not None:
        return session['oauth_token'], session['oauth_token_secret']

@kakao.tokengetter
def get_kakao_token():
    user = g.user
    if user is not None:
        return session['oauth_token']

@app.route('/logout')
def logout():
    session.clear()
    print(f'session cleared: {session}')
    return redirect(request.referrer or url_for('index'))

@app.route('/')
def index():
    tweets = None
    kakao_user_info = None

    if g.user is not None:
        resp = twitter.get('statuses/home_timeline.json')
        kakao_resp = kakao.get('user/me')

        if resp.status == 200 and session['platform'] == 'twitter':
            tweets = resp.data
        elif kakao_resp.status == 200 and session['platform'] == 'kakao':
            kakao_user_info = kakao_resp.data
        else:
            flash('소셜 플랫폼에서 데이터 로드가 불가능합니다.')

    return render_template('index.html', tweets=tweets, kakao_user_info=kakao_user_info)

@app.route('/twitter-login')
def twitter_login():
    url_for_res = url_for(
        'oauth_authorized',
        next=request.args.get('next') or request.referrer or None
    )
    session['platform'] = 'twitter'  # db insert시 플랫폼 구분 용도로 사용
    return twitter.authorize(callback=url_for_res)

@app.route('/kakao-login')
def kakao_login():
    """kakao dev callback uri 패턴: f'{base_url}/oauth-authorized'
    oauth를 승인하는 route에 맞춰서 지정한다.
    """
    url_for_res = url_for(
        'oauth_authorized',
        _external=True
    )
    session['platform'] = 'kakao'  # db insert시 플랫폼 구분 용도로 사용
    return kakao.authorize(callback=url_for_res)

@app.route('/oauth-authorized')
def oauth_authorized(resp=None):
    if session['platform'] == 'twitter':
        resp = twitter.authorized_response()
    elif session['platform'] == 'kakao':
        resp = kakao.authorized_response()

    resp = common.map_auth_response_key(resp, session['platform'])

    next_url = request.args.get('next') or url_for('index')
    if resp is None:
        flash(u'로그인 권한 없음')
        return redirect(next_url)


    user = db_session.query(User).filter_by(user_id=resp['user_id']).first()
    if user is None:
        user = User(
            platform=session['platform'],
            screen_name=resp['screen_name'],
            user_id=resp['user_id']
        )
        db_session.add(user)
    else:
        user.screen_name = resp['screen_name']
        user.update_date = datetime.now()
        db_session.merge(user)

    db_session.commit()

    session['user_id'] = user.user_id
    session['oauth_token'] = resp['oauth_token']
    session['oauth_token_secret'] = resp['oauth_token_secret']

    print(f'authorized session: {session}')
    flash('로그인되었습니다.')

    return redirect(next_url)

if __name__ == '__main__':
    app.run()
