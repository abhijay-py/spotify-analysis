import requests
import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

AUTH_URL = "https://accounts.spotify.com/api/token"
auth_response = requests.post(AUTH_URL, {
    'grant_type': 'client_credentials',
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
})

#Convert response to JSON
auth_response_data = auth_response.json()

#Save the access token
access_token = auth_response_data['access_token']

#Need to pass access token into header to send properly formed GET request to API server
headers = {
    'Authorization': 'Bearer {token}'.format(token=access_token)
}

BASE_URL = 'https://api.spotify.com/v1/'

#API CALLS

def get_track(id):
    r = requests.get(BASE_URL + f'tracks/{id}', headers=headers)
    r = r.json()
    return r

def get_tracks(id_list):
    r = requests.get(BASE_URL + f'tracks?ids={"%2C".join(id_list)}', headers=headers)
    r = r.json()
    return r

#API WRAPPERS

#Returns [album_uri_id, album_release, album_type, album_artists_out], artist_out [(id, name)], duration
def get_track_info(id):
    r = get_track(id)

    album_uri_id = r["album"]["id"]
    album_release = r["album"]["release_date"]
    album_type = r["album"]["type"]
    album_artists = r["album"]["artists"]
    album_artists_out = []
    for i in album_artists:
        album_artists_out.append((i["id"], i["name"]))

    album_out = [album_uri_id, album_release, album_type, album_artists_out]

    artists = r["artists"]
    artist_out = []
    for i in artists:
        artist_out.append((i["id"], i["name"]))

    duration = r["duration_ms"]

    return album_out, artist_out, duration


