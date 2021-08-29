from django.shortcuts import render
from django.http import HttpResponse
import requests
import base64
import os
import urllib
from .forms import YearAndUserNameForm
from .services import Wrapped
from datetime import date

CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')

REDIRECT_URI = 'http://127.0.0.1:8000/app/'

SCOPE = 'playlist-modify-public'

def make_url():
    base = 'https://accounts.spotify.com/authorize?'
    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'scope': SCOPE
    }
    return base + urllib.parse.urlencode(params)

def home(request):
    token = request.COOKIES.get('access_token', '')
    attempted = False
    success = False
    playlist = ''
    failures = []
    form = YearAndUserNameForm()

    if request.method == 'GET':
        if code := request.GET.get('code', ''):
            token = get_access_token(code)

        elif token != '':
            form = YearAndUserNameForm({'token': token, 'year': str(date.today().year - 1), 'is_own': False})

    elif request.method == 'POST' and token != '':
        success, playlist, failures = make_playlist(request, token)
        attempted = True

    context = {
        'spotify_url': make_url(),
        'is_authed': token != '',
        'success': success,
        'form': form,
        'attempted': attempted,
        'playlist_link': playlist,
        'failures': failures,
    }

    response = render(request, 'home.html', context=context)

    if token != '':
        response.set_cookie('access_token', token, max_age=3600)

    return response

def get_access_token(code):
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }

    headers = {
        'Authorization': 'Basic ' + base64.b64encode((CLIENT_ID + ':'+ CLIENT_SECRET).encode('ascii')).decode('ascii')
    }

    response = requests.post('https://accounts.spotify.com/api/token', data=data, headers=headers)

    token = ''
    if response.status_code == 200:
        token = response.json().get('access_token', '')

    return token

def make_playlist(request, token):
    username = request.POST.get('username')
    year = request.POST.get('year')
    is_own = request.POST.get('is_own')

    return Wrapped(username, is_own, year, SCOPE, token).create_playlists()