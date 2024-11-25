#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from collections import Counter

# Configuración de Flask
app = Flask(__name__)
CORS(app)

# Configuración de Spotify
SPOTIPY_CLIENT_ID = '2b6344bea92b45eb9a50ae1b65fa7507'
SPOTIPY_CLIENT_SECRET = '8815438da84a409895d943a6a5c35e00'
SPOTIPY_REDIRECT_URI = 'http://localhost:5000/callback'

sp_oauth = SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope="playlist-read-private"
)

@app.route('/')
def home():
    """Página principal"""
    return render_template('index.html')

@app.route('/authorize')
def authorize():
    """Autenticación con Spotify"""
    auth_url = sp_oauth.get_authorize_url()
    return jsonify({"auth_url": auth_url})

@app.route('/callback')
def callback():
    """Procesar autorización de Spotify"""
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    return jsonify(token_info)

@app.route('/analyze', methods=['POST'])
def analyze_playlist():
    """Analizar una playlist"""
    data = request.json
    playlist_id = data.get('playlist_id')

    if not playlist_id:
        return jsonify({"error": "No se proporcionó playlist_id"}), 400

    try:
        sp = spotipy.Spotify(auth=sp_oauth.get_cached_token()["access_token"])
        results = sp.playlist_items(playlist_id, limit=100)

        # Procesar canciones y artistas
        artistas = []
        for item in results['items']:
            track = item['track']
            if track:
                for artist in track['artists']:
                    artistas.append(artist['name'])

        # Contar artistas
        conteo_artistas = Counter(artistas).most_common(10)
        return jsonify({"top_artists": conteo_artistas})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

