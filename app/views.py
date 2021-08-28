from django.shortcuts import render
import requests
import base64
import os
import urllib
from . import forms
from . import services

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

    is_authed = False
    attempted = False
    success = False
    playlist = ''
    form = forms.YearAndUserNameForm()

    if request.method == 'GET':
        if code := request.GET.get('code', ''):
            data = {
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': REDIRECT_URI
            }

            headers = {
                'Authorization': 'Basic ' + base64.b64encode((CLIENT_ID + ':'+ CLIENT_SECRET).encode('ascii')).decode('ascii')
            }

            response = requests.post('https://accounts.spotify.com/api/token', data=data, headers=headers)

            if (is_authed := response.status_code == 200):
                access_token = response.json().get('access_token')
                form = forms.YearAndUserNameForm({'token': access_token})

    elif request.method == 'POST':
        username = request.POST.get('username')
        year = request.POST.get('year')
        access_token = request.POST.get('token')

        attempted = True
        wrapped = services.Wrapped(username, year, SCOPE, access_token)
        success, playlist = wrapped.create_playlists()

    context = {
        'spotify_url': make_url(),
        'is_authed': is_authed,
        'success': success,
        'form': form,
        'attempted': attempted,
        'playlist_link': playlist
    }

    print(request.method)
    print(success, playlist)

    return render(request, 'home.html', context=context)