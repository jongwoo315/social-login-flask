# social-login-flask

## Table of Contents
* [General Info](#general-information)
* [Technologies Used](#technologies-used)
* [Setup](#setup)
* [Usage](#usage)

## General Information
- flask로 구현한 트위터, 카카오 로그인
- mac os monterey 한정 이슈
    - 5000 포트는 airplay에서 사용중이므로 사용 불가능
- config.py.default
    - config.py로 파일명 변경 필요
    - 사용할 database uri와 api key 입력
    - app.py(line 8)와 models/model.py(line 7)에 사용할 class 명시

## Technologies Used
- python - 3.9
- flask - 2.1.2
- sqlalchemy - 1.4.39
- pymysql - 1.0.2

## Setup
```
$ pipenv shell --python 3.9
$ python -V
$ pipenv install
```

## Usage
```
$ flask run --port 5001
```

## Sources
- https://github.com/mitsuhiko/flask-oauth
- https://github.com/lepture/flask-oauthlib